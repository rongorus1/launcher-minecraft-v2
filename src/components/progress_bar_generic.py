from customtkinter import CTkProgressBar, CTkLabel


class ProgressBarGeneric(CTkProgressBar):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.is_hidden = True

        self.configure(
            fg_color=("#3a3a3a", "#3a3a3a"),
            progress_color=("#2ecc71", "#2ecc71"),
            width=1200,
            height=28,
            corner_radius=14
        )

        self.percent_label = CTkLabel(
            master,
            text="0 %",
            font=("Arial", 14, "bold"),
            text_color=("#ffffff", "#ffffff")
        )

        self.status_label = CTkLabel(
            master,
            text="",
            font=("Arial", 13),
            text_color=("#d0d0d0", "#d0d0d0")
        )

        self.set(0)

    def set(self, value):
        super().set(value)
        percent = int(max(0.0, min(1.0, float(value))) * 100)
        self.percent_label.configure(text=f"{percent} %")

    def set_status(self, text):
        self.status_label.configure(text=text)

    def update_width(self, width):
        self.configure(width=width)

    def _run_in_main(self, func):
        """Ejecuta una operacion de UI en el hilo principal (seguro desde hilos)."""
        try:
            self.master.after(0, func)
        except Exception:
            pass

    def set_thread_safe(self, value):
        self._run_in_main(lambda: self.set(value))

    def set_status_thread_safe(self, text):
        self._run_in_main(lambda: self.set_status(text))

    def show_element_thread_safe(self):
        self._run_in_main(self.show_element)

    def hidde_element_thread_safe(self):
        self._run_in_main(self.hidde_element)

    def show_element(self):
        self.place(
            relx=0.5,
            rely=0.00,
            anchor="center"
        )
        self.percent_label.place(
            relx=0.5,
            rely=0.06,
            anchor="center"
        )
        self.status_label.place(
            relx=0.5,
            rely=0.12,
            anchor="center"
        )
        self.is_hidden = False

    def hidde_element(self):
        self.place_forget()
        self.percent_label.place_forget()
        self.status_label.place_forget()
        self.is_hidden = True