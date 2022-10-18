from pathlib import Path


# Helper functions


def tree(directory):
    # Directory Tree
    print(f'+ {directory}')
    for path in sorted(directory.rglob('*')):
        depth = len(path.relative_to(directory).parts)
        spacer = '    ' * depth
        print(f'{spacer}+ {path.name}')


if __name__ == '__main__':
    rootdataDir = Path("./datax")
    # print(rootdataDir.resolve())
    bboxDir = rootdataDir / 'bbox_txt'
    try:
        bboxDir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("Folder is already there")
    else:
        print("Folder was created")

    imagesDir = rootdataDir / 'images'
    try:
        imagesDir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("Folder is already there")
    else:
        print("Folder was created")

    # moving text files to appropriate folder
    for txt_file in rootdataDir.glob('*.txt'):
        base = txt_file.name
        dest = bboxDir / base
        txt_file.rename(dest)

    # moving image files to appropriate folder
    for img_file in rootdataDir.glob('*.jpg'):
        base = img_file.name
        dest = imagesDir / base
        img_file.rename(dest)

    # print(tree(rootdataDir))
    print("Successfully ran the data sort")
