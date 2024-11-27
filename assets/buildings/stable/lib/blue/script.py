import os

# Define the folder containing the files
folder_path = "."

# Gather all files in the folder
files = [f for f in os.listdir(folder_path) if f.endswith("_stable.png")]

# Sort the files for consistent renaming
files.sort()

# Rename the files
for index, old_name in enumerate(files):
    # Generate the new name based on the index
    new_name = f"0_0x{index}_stable.png"
    old_path = os.path.join(folder_path, old_name)
    new_path = os.path.join(folder_path, new_name)
    
    # Rename the file
    os.rename(old_path, new_path)
    print(f"Renamed: {old_name} -> {new_name}")

print("Renaming completed.")
