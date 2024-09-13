"""
File with different helper functions
"""
from pathlib import Path
import tarfile
import numpy as np


def find_files_with_same_pattern(path: Path, pattern: str) -> list[str]:
    """
    Find files in the given path that match the specified pattern.

    Args:
        path (Path): The path to search for files.
        pattern (str): The pattern to match against file names.

    Returns:
        list[str]: A list of file paths that match the specified pattern.
    """
    search_directory = Path(path)
    search_pattern = sorted(search_directory.glob(pattern))

    return list(search_pattern)


def extract_a_file_from_tar(tar_file: Path, file_to_extract: str, output_dir: Path) -> None:
    """
    Extract a file from a tar file to the specified output directory.

    Args:
        tar_file (Path): The tar file to extract from.
        file_to_extract (str): The file to extract from the tar file.
        output_dir (Path): The directory to extract the file to.

    Returns:
        None
    """
    with tarfile.open(tar_file, 'r') as tar:
        tar.extract(file_to_extract, output_dir)


def create_folder(path: str, folder_name: str = "results") -> None:
    """
    Create a new folder at the specified path.

    Args:
        path (str): The path where the new folder should be created.
        folder_name (str, optional): The name of the new folder. Defaults to "results".

    Returns:
        None
    """
    # Specify the path of the new folder
    folder_path = Path(f'{path}/{folder_name}')

    # Use the mkdir method to create the folder
    folder_path.mkdir(parents=True, exist_ok=True)

def read_xvg_files(file_path: str):
    """
    Read data from an XVG file and return it as a NumPy array.

    Parameters:
    file_path (str): The path to the XVG file.

    Returns:
    numpy.ndarray: The data from the XVG file as a NumPy array.
    """
    data = []

    with open(file_path, 'r', encoding='utf8') as file:
        for line in file:

            if line.startswith('#') or line.startswith('@'):
                continue

            values = [float(val) for val in line.strip().split()]
            data.append(values)

    data_array = np.array(data, dtype=float)
    return data_array

def extract_tar_files():
    # Function to decompress specific files from a tar file
    # Extract the tar file
    tar_file = tarfile.open("data.tar.gz")
    tar_file.extractall()
    tar_file.close()
    # Extract the files from the tar file
    extract_a_file_from_tar("data.tar.gz", "file1.txt", "output_folder")
