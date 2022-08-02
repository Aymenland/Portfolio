from PIL import Image, ImageTk
from numpy import asarray, array, uint8, abs, sum as npsum, power
import os
from threading import Thread
from tkinter import Tk, Button, Frame, Label, Text, EW, END
from tkinter import filedialog


nw = 15  # Number of splits along the width
nh = 15  # Number of splits along the height


def average_color(pixels):
    color_sum = [0, 0, 0]
    n = 0
    for row in pixels:
        for pixel in row:
            n += 1
            try:
                color_sum = [color_sum[0] + pixel[0], color_sum[1] + pixel[1], color_sum[2] + pixel[2]]
            except IndexError:
                color_sum = [color_sum[0] + pixel, color_sum[1] + pixel, color_sum[2] + pixel]

    return [int(color_sum[0] / n), int(color_sum[1] / n), int(color_sum[2] / n)]


class App:
    def __init__(self, master):
        frame = Frame(master, bg="#BBBBBB", borderwidth=1, padx=5, pady=5)
        frame.grid(row=0, column=0)
        self.images = []

        # Database

        Button(frame, text="Initialize\nDatabase", font="Arial 13", width=15, borderwidth=1, bg="#CCCCFF",
               activebackground="#CCCCFF", command=self.mid_init)\
            .grid(row=0, column=0, padx=5, pady=5, sticky=EW)
        Button(frame, text="Updated\nDatabase", font="Arial 13", width=15, borderwidth=1, bg="#CCCCFF",
               activebackground="#CCCCFF", command=self.mid_upd)\
            .grid(row=0, column=1, padx=5, pady=5, sticky=EW)

        # Image Uploading

        Button(frame, text="Load Images", font="Arial 13", width=15, borderwidth=1, bg="#CCCCFF",
               activebackground="#CCCCFF", command=self.mid_load) \
            .grid(row=1, column=0, padx=5, pady=5, sticky=EW)

        Button(frame, text="Upload Image &\nSearch for Match", font="Arial 13", width=15, borderwidth=1, bg="#CCCCFF",
               activebackground="#CCCCFF", command=self.mid_search)\
            .grid(row=1, column=1, padx=5, pady=5, sticky=EW)

        self.uploaded_image = Text(frame, font="Arial 10", bd=1, relief="sunken", bg="#CCCCCC", fg="#444",
                                   height=1, width=15, padx=2, pady=3)
        self.uploaded_image.configure(state="disabled")
        self.uploaded_image.configure(inactiveselectbackground=self.uploaded_image.cget("selectbackground"))
        self.uploaded_image.tag_configure("center", justify='center')
        self.uploaded_image.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=EW)
        self.uploaded_image.tag_configure("center", justify='center')

        # Search Results

        self.result_image = Label(frame, bd=1, relief="sunken")
        self.result_image_path = Text(frame, font="Arial 10", bd=1, relief="sunken", bg="#CCCCCC", fg="#444",
                                      height=3, width=15, padx=2, pady=3)
        self.result_image_path.configure(state="disabled")
        self.result_image_path.configure(inactiveselectbackground=self.result_image_path.cget("selectbackground"))
        self.result_image_path.tag_configure("center", justify='center')

    def mid_init(self):
        Thread(target=self.initialize_db).start()

    def mid_upd(self):
        Thread(target=self.updated_db).start()

    def mid_search(self):
        """lp = LineProfiler()
        lp_wrapper = lp(self.search)
        lp_wrapper()
        lp.print_stats()"""
        Thread(target=self.search).start()

    def mid_load(self):
        Thread(target=self.load_images).start()

    def initialize_db(self):
        self.result_image.grid_forget()
        self.result_image_path.grid_forget()

        rootdir = filedialog.askdirectory(initialdir=os.getcwd())

        self.uploaded_image.configure(state="normal")
        self.uploaded_image.delete("1.0", END)
        self.uploaded_image.insert(1.0, "Analyzing...")
        self.uploaded_image.configure(state="disabled")
        self.uploaded_image.tag_add("center", "1.0", END)

        f = open('images_compressed', 'w')

        n = 0
        for file in os.listdir(rootdir):
            n += 1
            img = Image.open(rootdir + "/" + file)
            img_array = asarray(img)

            new_img_width = len(img_array[0]) / nw
            new_img_height = len(img_array) / nh

            new_img_array = array([
                [
                    average_color(
                        img_array[int(i * new_img_height): int((i + 1) * new_img_height),
                        int(j * new_img_width): int((j + 1) * new_img_width)]
                    ) for j in range(nw)
                ] for i in range(nh)
            ], uint8)

            text = " ".join(str(elem) for elem in new_img_array.flatten())
            f.write(rootdir + "/" + file + "::" + text.strip() + "\n")

            if n % 100 == 0:
                self.uploaded_image.configure(state="normal")
                self.uploaded_image.delete("1.0", END)
                self.uploaded_image.insert(1.0, str(n) + " images have been analyzed.")
                self.uploaded_image.tag_add("center", "1.0", END)
                self.uploaded_image.configure(state="disabled")

        self.uploaded_image.configure(state="normal")
        self.uploaded_image.delete("1.0", END)
        self.uploaded_image.insert(1.0, "Finished." + str(n) + " images have been analyzed.")
        self.uploaded_image.configure(state="disabled")
        self.uploaded_image.tag_add("center", "1.0", END)

    def updated_db(self):
        self.result_image.grid_forget()
        self.result_image_path.grid_forget()

        rootdir = filedialog.askdirectory(initialdir=os.getcwd())

        text = open('images_compressed', 'r').read()
        f = open("images_compressed", "a")

        self.uploaded_image.configure(state="normal")
        self.uploaded_image.delete("1.0", END)
        self.uploaded_image.insert(1.0, "Analyzing...")
        self.uploaded_image.tag_add("center", "1.0", END)
        self.uploaded_image.configure(state="disabled")

        n = 0
        for file in os.listdir(rootdir):
            if rootdir + "/" + file in text:
                continue

            n += 1
            img = Image.open(rootdir + "/" + file)
            img_array = asarray(img)

            new_img_width = len(img_array[0]) / nw
            new_img_height = len(img_array) / nh

            new_img_array = array([
                [
                    average_color(
                        img_array[int(i * new_img_height): int((i + 1) * new_img_height),
                        int(j * new_img_width): int((j + 1) * new_img_width)]
                    ) for j in range(nw)
                ] for i in range(nh)
            ], uint8)

            text = " ".join(str(elem) for elem in new_img_array.flatten())
            f.write(rootdir + "/" + file + "::" + text.strip() + "\n")

            if n % 100 == 0:
                self.uploaded_image.configure(state="normal")
                self.uploaded_image.delete("1.0", END)
                self.uploaded_image.insert(1.0, str(n) + " new images have been analyzed.")
                self.uploaded_image.tag_add("center", "1.0", END)
                self.uploaded_image.configure(state="disabled")

        self.uploaded_image.configure(state="normal")
        self.uploaded_image.delete("1.0", END)
        self.uploaded_image.insert(1.0, "Finished." + str(n) + " new images have been analyzed.")
        self.uploaded_image.configure(state="disabled")
        self.uploaded_image.tag_add("center", "1.0", END)

    def load_images(self):
        self.result_image.grid_forget()
        self.result_image_path.grid_forget()

        self.uploaded_image.configure(state="normal")
        self.uploaded_image.delete("1.0", END)
        self.uploaded_image.insert(1.0, "Loading...")
        self.uploaded_image.configure(state="disabled")
        self.uploaded_image.tag_add("center", "1.0", END)

        with open("images_compressed", "r") as file:
            text = file.read().strip().split("\n")
            self.images = [[line.split("::", maxsplit=1)[0], line.split("::", maxsplit=1)[1].split(" ")]
                           for line in text]
            self.images = [[image[0], array([int(elem) for elem in image[1]])] for image in self.images]

        self.uploaded_image.configure(state="normal")
        self.uploaded_image.delete("1.0", END)
        self.uploaded_image.insert(1.0, "Finished.")
        self.uploaded_image.configure(state="disabled")
        self.uploaded_image.tag_add("center", "1.0", END)

    def search(self):
        self.result_image.grid_forget()
        self.result_image_path.grid_forget()

        if not self.images:
            self.uploaded_image.configure(state="normal")
            self.uploaded_image.delete("1.0", END)
            self.uploaded_image.insert(1.0, "Images are not loaded yet.")
            self.uploaded_image.configure(state="disabled")
            self.uploaded_image.tag_add("center", "1.0", END)
            return

        image_path = filedialog.askopenfilename(initialdir=os.getcwd())

        self.uploaded_image.configure(state="normal")
        self.uploaded_image.delete("1.0", END)
        self.uploaded_image.insert(1.0, "Analyzing...")
        self.uploaded_image.configure(state="disabled")
        self.uploaded_image.tag_add("center", "1.0", END)

        img1 = Image.open(image_path)
        img1_array = asarray(img1)

        new_img1_width = len(img1_array[0]) / nw
        new_img1_height = len(img1_array) / nh

        new_img1_array = array([
            [
                average_color(
                    img1_array[int(i * new_img1_height): int((i + 1) * new_img1_height),
                    int(j * new_img1_width): int((j + 1) * new_img1_width)]
                ) for j in range(nw)
            ] for i in range(nh)
        ], uint8)

        error_list = {}

        shortlist_len = 50
        images_shortlist = []

        for image in self.images:
            error = npsum(power(abs(new_img1_array.flatten() - image[1]), 2))

            if error == 0:
                self.uploaded_image.configure(state="normal")
                self.uploaded_image.delete("1.0", END)
                self.uploaded_image.insert(1.0, "Finished.")
                self.uploaded_image.configure(state="disabled")
                self.uploaded_image.tag_add("center", "1.0", END)

                result_path = image[0]
                result_image = Image.open(result_path)
                result_image = ImageTk.PhotoImage(result_image)

                self.result_image.image = result_image
                self.result_image.configure(image=result_image)
                self.result_image.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=EW)

                self.result_image_path.configure(state="normal")
                self.result_image_path.delete("1.0", END)
                self.result_image_path.insert(1.0, result_path)
                self.result_image_path.configure(state="disabled")
                self.result_image_path.tag_add("center", "1.0", END)
                self.result_image_path.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=EW)
                return

            if len(images_shortlist) < shortlist_len:
                images_shortlist.append((image, error))
            elif len(images_shortlist) == shortlist_len:
                m = max(images_shortlist, key=lambda x: x[1])
                if m[1] > error:
                    images_shortlist.append((image, error))
                    images_shortlist.remove(m)

        for image in images_shortlist:
            img2_array = image[0][1]

            error = 0
            n = 0
            for row in new_img1_array:
                for pixel in row:
                    error += abs(pixel[0] - img2_array[n]) ** 2 + abs(pixel[1] - img2_array[n + 1]) ** 2 + abs(
                        pixel[2] - img2_array[n + 2]) ** 2
                    n += 3

            error_list[image[0][0]] = error
            if error <= 100:
                self.uploaded_image.configure(state="normal")
                self.uploaded_image.delete("1.0", END)
                self.uploaded_image.insert(1.0, "Finished.")
                self.uploaded_image.configure(state="disabled")
                self.uploaded_image.tag_add("center", "1.0", END)

                result_path = image[0][0]
                result_image = Image.open(result_path)
                result_image = ImageTk.PhotoImage(result_image)

                self.result_image.image = result_image
                self.result_image.configure(image=result_image)
                self.result_image.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=EW)

                self.result_image_path.configure(state="normal")
                self.result_image_path.delete("1.0", END)
                self.result_image_path.insert(1.0, result_path)
                self.result_image_path.configure(state="disabled")
                self.result_image_path.tag_add("center", "1.0", END)
                self.result_image_path.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=EW)
                return

        self.uploaded_image.configure(state="normal")
        self.uploaded_image.delete("1.0", END)
        self.uploaded_image.insert(1.0, "Finished.")
        self.uploaded_image.configure(state="disabled")
        self.uploaded_image.tag_add("center", "1.0", END)

        result_path = min(error_list, key=lambda x: error_list[x])
        result_image = Image.open(result_path)
        result_image = ImageTk.PhotoImage(result_image)

        self.result_image.image = result_image
        self.result_image.configure(image=result_image)
        self.result_image.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=EW)

        self.result_image_path.configure(state="normal")
        self.result_image_path.delete("1.0", END)
        self.result_image_path.insert(1.0, result_path)
        self.result_image_path.configure(state="disabled")
        self.result_image_path.tag_add("center", "1.0", END)
        self.result_image_path.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=EW)


# -----> App Execution <----- #

if __name__ == "__main__":
    root = Tk()
    root.title("Made by Aymen")
    root.iconbitmap("ico.ico")
    root.resizable(width=False, height=False)
    game = App(root)
    root.mainloop()
