import os
def main():
    os.system("uvicorn cyo.main:app --reload")
    print("Hello from backend!")


if __name__ == "__main__":
    main()
