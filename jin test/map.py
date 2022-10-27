import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

path = "camera_data/"
fname = "all_cameras_ids_locations.csv"
df = pd.read_csv(f"{path}{fname}")

# import our image 
map_fname = "singapore_map.png"
bnw_fname = "singapore_bnw.png"
singapore_map = mpimg.imread(f"{path}{map_fname}")
singapore_bnw = mpimg.imread(f"{path}{bnw_fname}")

# plot the data
ax = df.plot(
    kind="scatter", 
    x="long", 
    y="lat", 
    color = "red",
    figsize=(20,14),
    cmap=plt.get_cmap("jet"),
    alpha=0.8,
)

# plot map
save_map = "singapore_camera_map"
plt.imshow(singapore_map, extent=[103.5,104,1.15, 1.50])    
plt.ylabel("Latitude", fontsize=20)
plt.xlabel("Longitude", fontsize=20)
plt.ylim(1.15, 1.50)
plt.xlim(103.5, 104)
plt.savefig(f"{path}{save_map}")

# plot black and white map
save_bnw = "singapore_camera_bnw"
plt.imshow(singapore_bnw, extent=[103.5,104,1.15, 1.50])    
plt.ylabel("Latitude", fontsize=20)
plt.xlabel("Longitude", fontsize=20)
plt.ylim(1.15, 1.50)
plt.xlim(103.5, 104)
plt.savefig(f"{path}{save_bnw}")

