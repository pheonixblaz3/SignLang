import os

def verify_tag_file(tag_path: str = r"C:\Users\medhu\Desktop\backend\green\encrypt\project.tag") -> bool:
    """
    Checks if the .tag file exists and contains the expected content.
    Returns True if valid, False otherwise.
    """
    EXPECTED_CONTENT = "Made By Abhigyan Singh(Contributers: Medhansh n Arsh)"

    if not os.path.exists(tag_path):
        return False

    try:
        with open(tag_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return content == EXPECTED_CONTENT
    except Exception:
        return False
