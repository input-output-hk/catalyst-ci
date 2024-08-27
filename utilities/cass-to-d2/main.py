import sys
import os

def extract_src(src_dir: str):
    if not os.path.isdir(src_dir):
        raise Exception(f"'{src_dir}' is not directory.")
    
    # Get the list of files in the directory
    files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]

    for file in files:
        extract_file(os.path.join(src_dir, file))

def extract_file(file_path: str):
    print(file_path)

def main():
    if len(sys.argv) != 3:
        raise Exception("The command requires two arguments to execute <src-dir> and <out-dir>.")

    [ prog, src_dir, out_dir ] = sys.argv

    abs_src_dir = os.path.abspath(src_dir)
    abs_out_dir = os.path.abspath(out_dir)

    extract_src(abs_src_dir)

if __name__ == "__main__":
    main()
