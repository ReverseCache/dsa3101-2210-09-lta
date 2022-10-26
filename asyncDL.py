import threading
import time
import requests
import os
image_url_list = [
    "https://i.picsum.photos/id/681/200/300.jpg?hmac=RrSjLfU9adr2teGTAalv7b6XXsDyaPxIWyoBm30Qn5A",
    "https://i.picsum.photos/id/726/200/300.jpg?hmac=9WbqvM6W7D0BwVEyvVbC2xL9ulSQpXyoTcL3O89modM",
    "https://i.picsum.photos/id/1002/200/300.jpg?hmac=QAnT71VGihaxEf_iyet9i7yb3JvYTzeojsx-djd3Aos",
    "https://i.picsum.photos/id/997/200/300.jpg?hmac=NeXq5MvhpKvGEq_X3jULp2C3Lg-8IQK8bdtnyJeXDIQ",
    "https://i.picsum.photos/id/610/200/300.jpg?hmac=O1d50QqoBFGhSj9Hd8cdWjPlhPJEMWFE8HRsHArsnfk",
    "https://i.picsum.photos/id/154/200/300.jpg?hmac=9yMwkzYXuJYDbG15-lORLjtqCiAQiBd6wDIKPBiJBM8",
    "https://i.picsum.photos/id/680/200/300.jpg?hmac=OUdNxaSLxw8SgCxALPFPfZAurK6KVGLpU3hzbCrumJc",
    "https://i.picsum.photos/id/402/200/300.jpg?hmac=JmZsqnQgJgxs4tbKwb8Tdu3r-B0tEGN7nrKEb1jBB0Y",
    "https://i.picsum.photos/id/302/200/300.jpg?hmac=b5e6gUSooYpWB3rLAPrDpnm8PsPb84p_NXRwD-DK-1I",
    "https://i.picsum.photos/id/101/200/300.jpg?hmac=xUDvORQTxaML0fp9wnx4y6LIHvc7M-tNcOJz8rDLRXo",
    "https://i.picsum.photos/id/640/200/300.jpg?hmac=wFv1Wyd-STy0zsr2E2USifr--6VcaWg6pOhzelisMIg",
    "https://i.picsum.photos/id/937/200/300.jpg?hmac=e85ZMdNwmCfn1FopDunIZzaSxZC2-lC9qsLqb6V0xpQ",
    "https://i.picsum.photos/id/250/200/300.jpg?hmac=igVdxs-AgITpHwPAZ80mpAfmhrGBvN_xThJlhp7vOqE",
    "https://i.picsum.photos/id/736/200/300.jpg?hmac=WlU1DEqIVU_kIsTa682WsLgBIfCRbqhOAuKifGAq8TY",
    "https://i.picsum.photos/id/14/200/300.jpg?hmac=FMdb1SH_oeEo4ibDe66-ORzb8p0VYJUS3xWfN3h2qDU",
    "https://i.picsum.photos/id/853/200/300.jpg?hmac=-vUTO-GMdNHJbNIJrZtC4jsw0ybpHVgCrtWkg1DZugg",
    "https://i.picsum.photos/id/176/200/300.jpg?hmac=FVhRySTQhcAO5Xvxk6nE-bMsJSyIAW8Uw6zWgAh9hzY",
    "https://i.picsum.photos/id/238/200/300.jpg?hmac=WF3u-tnO4aoQvz_F9p7zS0Dr5LwGx74tPabQf7EjHkw",
    "https://i.picsum.photos/id/829/200/300.jpg?hmac=stRF7eyl9bbNtU_2pkkEwP-jV_upn27-hWuLQG4maMU",
    "https://i.picsum.photos/id/194/200/300.jpg?hmac=jZgjsqqVvdWnXHdytjS2JPImgQFz9bGSyVQ31-b_eH4",
    "https://i.picsum.photos/id/178/200/300.jpg?hmac=o3W6XkZMX-Pv9EKaOaE6vvt4JpToHfjivAGRrpFuhiw",
    "https://i.picsum.photos/id/691/200/300.jpg?hmac=1nouilaOHm3p-SqXPrCLcCcFEtJ60GlDAwkLAHq4x-c",
    "https://i.picsum.photos/id/585/200/300.jpg?hmac=9pIkZ1OAqMKxQt7_5yNLOWAjZBmJ99k53TBNs3xQQe4",
    "https://i.picsum.photos/id/617/200/300.jpg?hmac=WVwPHGFiGQ3OhdyeRk0pQ82EUCJuksc-Zf7YjirDr9Q",
    "https://i.picsum.photos/id/135/200/300.jpg?hmac=d3sTOCUkxdC1OKCgh9wTPjck-gMWATyVHFvflla5vLI",
    "https://i.picsum.photos/id/696/200/300.jpg?hmac=Ukxvga_1GYxgfAqzwDhBPfVta6-hJKUhayVlI1yMIdk"
]

# Making a new folder in the current dir.

os.mkdir("Images")
os.chdir(os.path.join(os.getcwd(), "Images"))


def download(url, name):
    r = requests.get(url)
    f = open(name, "wb")
    f.write(r.content)
    f.close()
    print(name)


t1 = time.time()

threads = []

# for i in range(len(image_url_list)):
#     download(image_url_list[i],f"{i+1}.png")

for i in range(len(image_url_list)):
    temp = threading.Thread(target=download, args=[
                            image_url_list[i], f"{i+1}.png"])
    temp.start()
    threads.append(temp)

for thread in threads:
    thread.join()

t2 = time.time()

print("Time takes : ", t2-t1)
