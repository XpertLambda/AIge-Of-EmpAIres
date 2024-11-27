import os

# Define the folder containing the files
folder_path = "."

# Gather all files in the folder that match the pattern
files = [f for f in os.listdir(folder_path) if f.startswith("0_1x") and f.endswith("_stable.png")]

# Sort the files for consistent renaming
files.sort()

# Rename the files
for index, old_name in enumerate(files):
    # Generate the new name by replacing the prefix and keeping the rest
    new_name = old_name.replace("0_1x", "1_0x")
    old_path = os.path.join(folder_path, old_name)
    new_path = os.path.join(folder_path, new_name)
    
    # Rename the file
    os.rename(old_path, new_path)
    print(f"Renamed: {old_name} -> {new_name}")

print("Renaming completed.")
