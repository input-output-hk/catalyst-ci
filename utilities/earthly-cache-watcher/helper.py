import os


def get_subdirectory_name(working_dir_path: str, path: str):
    """
    Extracts the direct subdirectory name from the given path within
    the specified working directory.

    Parameters:
    working_dir_path (str): The absolute path of the current working directory.
    path (str): The absolute path from which to extract the direct subdir name.

    Returns:
    str | None: The name of the direct subdirectory if the given path is within
                the working directory; otherwise, None.

    Example:
    >>> working_dir = "/home/user/projects"
    >>> given_path = "/home/user/projects/subdir1/file.txt"
    >>> get_subdirectory_name(working_dir, given_path)
    'subdir1'

    >>> given_path_invalid = "/home/user/projects1/subdir1/file.txt"
    >>> get_subdirectory_name(working_dir, given_path_invalid)
    None
    """
    working_dir_path = os.path.abspath(working_dir_path)
    path = os.path.abspath(path)

    if os.path.commonpath([working_dir_path]) != os.path.commonpath(
        [working_dir_path, path]
    ):
        return None

    relative_path = os.path.relpath(path, working_dir_path)
    parts = relative_path.split(os.sep)

    if parts:
        return parts[0]
    return None


def add_or_init(obj: dict[str, int], key: str, value: int):
    obj.setdefault(key, 0)
    obj[key] += value
