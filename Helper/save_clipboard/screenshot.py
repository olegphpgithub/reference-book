import sys
from pathlib import Path
from datetime import datetime
from PIL import ImageGrab


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <folder>")
        sys.exit(1)

    folder = Path(sys.argv[1])

    if not folder.is_dir():
        print(f"Folder does not exist: {folder}")
        sys.exit(1)

    image = ImageGrab.grabclipboard()

    if image is None:
        print("Clipboard does not contain an image.")
        sys.exit(1)

    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")
    output_path = folder / filename

    image.save(output_path, "PNG")
    print(output_path)


if __name__ == "__main__":
    main()