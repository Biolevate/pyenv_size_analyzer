import os
import sys
from pathlib import Path
from pip._internal.operations.freeze import freeze
from importlib.metadata import distributions, requires
import site
from collections import defaultdict

def get_site_packages_dirs():
    return site.getsitepackages()

def crawl_site_packages():
    total_size = 0
    directory_sizes = {}
    
    for site_packages in get_site_packages_dirs():
        for entry in os.scandir(site_packages):
            if entry.is_dir() or entry.is_file():
                try:
                    if entry.name.endswith(('.egg', '.whl')):
                        size = entry.stat().st_size
                    elif entry.is_dir():
                        size = get_directory_size(entry.path)
                    else:
                        size = entry.stat().st_size
                    total_size += size
                    directory_sizes[entry.name] = size
                except OSError as e:
                    print(f"Error accessing {entry.path}: {e}", file=sys.stderr)
    
    return total_size, directory_sizes

def get_directory_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path, followlinks=False):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def match_directories_to_packages(directory_sizes):
    package_sizes = {}
    unmatched_directories = {}
    
    # Create a mapping of normalized package names and their corresponding distribution names
    dir_to_dist = {}
    for dist in distributions():
        normalized_name = dist.metadata['Name'].lower().replace('-', '_')
        dir_to_dist[normalized_name] = dist.metadata['Name']
        if dist.files:
            top_level_dirs = {file.parts[0] for file in dist.files}
            for top_level_dir in top_level_dirs:
                dir_to_dist[top_level_dir.lower()] = dist.metadata['Name']

    for directory, size in directory_sizes.items():
        directory_lower = directory.lower()
        dist_name = None
        
        # Check for exact match
        if directory_lower in dir_to_dist:
            dist_name = dir_to_dist[directory_lower]
        
        
        # Check for .dist-info directories
        elif directory_lower.endswith('.dist-info'):
            dist_name = directory.rsplit('-', 2)[0].replace('_', '-')
        
        # Check for .egg-info directories
        elif directory_lower.endswith('.egg-info'):
            dist_name = directory.rsplit('.egg-info', 1)[0].replace('_', '-')
        
        # Check for .egg or .whl files
        elif directory_lower.endswith(('.egg', '.whl')):
            dist_name = directory.rsplit('-', 2)[0].replace('_', '-')
        
        # Check for partial matches
        else:
            for dir_name in dir_to_dist:
                if directory_lower.startswith(dir_name) or dir_name.startswith(directory_lower):
                    dist_name = dir_to_dist[dir_name]
                    break
        
        if dist_name:
            if dist_name in package_sizes:
                package_sizes[dist_name] += size
            else:
                package_sizes[dist_name] = size
        else:
            # Filter out common non-package files
            if not directory_lower.startswith('_virtualenv'):
                unmatched_directories[directory] = size
    
    return package_sizes, unmatched_directories

def get_package_dependencies():
    dependencies = defaultdict(set)
    required_by = defaultdict(set)
    for dist in distributions():
        if dist.requires:
            dependencies[dist.metadata['Name']] = set(dep.split()[0] for dep in dist.requires)
            for dep in dist.requires:
                required_by[dep.split()[0]].add(dist.metadata['Name'])
    return dependencies, required_by

def calculate_total_impact_for_roots(package_sizes, dependencies, required_by):
    total_impact = {}
    root_packages = {pkg for pkg in package_sizes if pkg not in required_by}

    def calculate_impact(pkg):
        stack = [pkg]
        visited = set()
        total_size = 0

        while stack:
            current_pkg = stack.pop()
            if current_pkg not in visited:
                visited.add(current_pkg)
                total_size += package_sizes.get(current_pkg, 0)
                stack.extend(dependencies.get(current_pkg, []))

        return total_size

    for package in root_packages:
        total_impact[package] = calculate_impact(package)
    
    return dict(sorted(total_impact.items(), key=lambda x: x[1], reverse=True))


def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def generate_report(exclude_packages=None, top_n=15):
    if exclude_packages is None:
        exclude_packages = []
    
    total_size, directory_sizes = crawl_site_packages()
    package_sizes, unmatched_directories = match_directories_to_packages(directory_sizes)
    
    # Remove excluded packages
    for package in exclude_packages:
        if package in package_sizes:
            del package_sizes[package]
    
    dependencies, required_by = get_package_dependencies()
    total_impact = calculate_total_impact_for_roots(package_sizes, dependencies, required_by)
    
    print("Package Sizes:")
    print_size_table(package_sizes, total_size, top_n)
    
    print("\nRoot Package Total Impact (including dependencies) -  WARNING it might overlap with other packages:")
    print_size_table(total_impact, total_size, top_n)
    
    if unmatched_directories:
        print("\nUnmatched Directories:")
        print_size_table(unmatched_directories, total_size, top_n)
    
    print("\nSummary:")
    print(f"{'Total Size:':<30} {format_size(total_size)}")
    matched_size = sum(package_sizes.values())
    unmatched_size = sum(unmatched_directories.values())
    print(f"{'Matched Size:':<30} {format_size(matched_size)} ({matched_size/total_size*100:.2f}%)")
    print(f"{'Unmatched Size:':<30} {format_size(unmatched_size)} ({unmatched_size/total_size*100:.2f}%)")

def print_size_table(size_dict, total_size, top_n):
    print(f"{'Name':<30} {'Size':<15} {'Percentage':<10}")
    print("-" * 55)

    # Calculate the sum for the top N and the others
    displayed_sum = 0
    others_sum = 0
    
    sorted_packages = sorted(size_dict.items(), key=lambda x: x[1], reverse=True)
    
    for i, (name, size) in enumerate(sorted_packages):
        if i < top_n:
            percentage = (size / total_size) * 100
            displayed_sum += size
            print(f"{name[:29]:<30} {format_size(size):<15} {percentage:.2f}%")
        else:
            others_sum += size
    
    # Print the "others" summary if there are more packages than top_n
    if len(size_dict) > top_n:
        others_percentage = (others_sum / total_size) * 100
        print(f"{'Others':<30} {format_size(others_sum):<15} {others_percentage:.2f}%")


if __name__ == "__main__":
    exclude_packages = ['pip', 'setuptools']
    generate_report(exclude_packages, top_n=15)
