from DesktopCompanion import DesktopCompanion

if __name__ == "__main__":    
    try:
        companion = DesktopCompanion()
        companion.run()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
