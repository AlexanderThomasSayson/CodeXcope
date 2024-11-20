import tkinter as tk
from tkinter import filedialog, messagebox
from src.data_processing.process_fund_transfer_logs import process_fund_transfer_logs
from src.data_processing.process_promotexter_logs import process_promotexter_data
from src.data_processing.process_rds_logs import process_rds_logs
from PIL import Image, ImageTk
from src.data_processing.create_summary import create_summary


# Function for the upload buttons
def upload_file(button):
    file_path = filedialog.askopenfilename()
    if file_path:
        if button == "Fund Transfer Logs":
            process_fund_transfer_logs(file_path)
        elif button == "RDS Logs":
            process_rds_logs(file_path)
        elif button == "Promotexter Logs":
            process_promotexter_data(file_path)
        messagebox.showinfo("Success!", f"{button} execution successful")


# Create gradient function
def create_gradient(canvas, color1, color2, width, height):
    for i in range(height):
        # Calculate the grayscale intensity for each line
        intensity = int(color1[0] + (color2[0] - color1[0]) * i / height)
        color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"  # Grayscale color
        canvas.create_line(0, i, width, i, fill=color)


# Create GUI
def create_gui():
    root = tk.Tk()
    root.title("CodeXCope")

    # Set window size and position
    window_width = 600
    window_height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Create canvas for gradient background
    canvas = tk.Canvas(root, width=window_width, height=window_height)
    canvas.pack(fill="both", expand=True)

    # Create gradient background (from dark grey to white)
    create_gradient(canvas, (64, 64, 64), (255, 255, 255), window_width, window_height)

    # Add logo (replace 'path_to_logo.png' with your actual logo path)
    logo = Image.open(r"src/img/codeXcope.png")
    logo = logo.resize((200, 150), Image.LANCZOS)
    logo = ImageTk.PhotoImage(logo)
    logo_label = tk.Label(canvas, image=logo, bg=canvas["bg"])
    logo_label.image = logo
    logo_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

    buttons = ["Fund Transfer Logs", "RDS Logs", "Promotexter Logs"]
    for i, button in enumerate(buttons):
        btn = tk.Button(
            canvas, text=f"Upload {button}", command=lambda b=button: upload_file(b)
        )
        btn.place(relx=0.5, rely=0.5 + i * 0.1, anchor=tk.CENTER)

    summary_btn = tk.Button(canvas, text="Create Summary", command=create_summary)
    summary_btn.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
