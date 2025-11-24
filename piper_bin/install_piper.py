#!/usr/bin/env python3
import os
import tarfile
import shutil

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tar_path = os.path.join(base_dir, "piper_linux_aarch64.tar.gz")
    extract_dir = os.path.join(base_dir, "piper")

    print("=== Piper Local Installer ===")
    print(f"Base directory: {base_dir}")
    print(f"Tarball:        {tar_path}")
    print(f"Extract target: {extract_dir}")
    print()

    # Check tarball exists
    if not os.path.exists(tar_path):
        print("ERROR: Tarball not found!")
        print("Expected at:")
        print(f"  {tar_path}")
        return

    # Remove old installation
    if os.path.exists(extract_dir):
        print("Removing old 'piper' directory...")
        shutil.rmtree(extract_dir)

    # Extract tarball
    print("Extracting Piper tarball...")
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(base_dir)
        print("\nExtraction complete!")
    except Exception as e:
        print("\nERROR during extraction:")
        print(str(e))
        return

    # Verify result
    if not os.path.isdir(extract_dir):
        print("\nWARNING: Piper directory not found after extraction.")
        print("Check tarball contents — it may extract to a different folder name.")
    else:
        print("\nPiper successfully extracted!")
        print(f"Piper binary should be located at:\n  {extract_dir}/piper")

    print("\nDone.")

if __name__ == "__main__":
    main()
