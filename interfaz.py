import tkinter as tk
from tkinter import ttk

import generadores as gen

# Paleta neutra
C = {
    "fondo": "#ECECEA",
    "panel": "#FAFAF9",
    "borde": "#D4D4D0",
    "texto": "#2E3236",
    "suave": "#6C7075",
    "acento": "#5B6770",
    "acento_hover": "#46515A",
    "fila_alt": "#F0F0EE",
    "seleccion": "#DADDDF",
}
FUENTE = ("Segoe UI", 10)


class PestanaMetodo(ttk.Frame):
    def __init__(self, master, clave):
        super().__init__(master, style="Panel.TFrame", padding=18)
        self.clave = clave
        self.n_var = tk.StringVar(value="10")
        info = gen.METODOS[clave]

        ttk.Label(self, text=info["nombre"], style="Titulo.TLabel").pack(anchor="w")
        desc = ttk.Label(self, text=info["descripcion"], style="Suave.TLabel",
                         wraplength=880, justify="left")
        desc.pack(anchor="w", pady=(2, 14), fill="x")

        # Barra de control
        barra = ttk.Frame(self, style="Panel.TFrame")
        barra.pack(fill="x")
        ttk.Label(barra, text="Cantidad de números (n):", style="Panel.TLabel").pack(side="left")
        spin = ttk.Spinbox(barra, from_=1, to=1000, width=6, textvariable=self.n_var,
                           command=self.ejecutar)
        spin.pack(side="left", padx=8)
        spin.bind("<Return>", lambda e: self.ejecutar())
        if clave in ("lineal", "multiplicativo"):
            spin.state(["disabled"])   # el periodo de vida define cuántos se generan
        ttk.Button(barra, text="Generar de nuevo", style="Acento.TButton",
                   command=self.ejecutar).pack(side="left", padx=8)

        # Parámetros
        self.marco_params = ttk.LabelFrame(self, text=" Parámetros aleatorios ", padding=10,
                                           style="Panel.TLabelframe")
        self.marco_params.pack(fill="x", pady=(14, 6))
        self.lbl_notas = ttk.Label(self, text="", style="Suave.TLabel", justify="left")
        self.lbl_notas.pack(anchor="w", pady=(0, 6))

        # Tabla
        cont = ttk.Frame(self, style="Panel.TFrame")
        cont.pack(fill="both", expand=True)
        self.tabla = ttk.Treeview(cont, show="headings", height=12)
        sb = ttk.Scrollbar(cont, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sb.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tabla.tag_configure("alt", background=C["fila_alt"])

        # Resultado final
        pie = ttk.LabelFrame(self, text=" Números pseudoaleatorios generados (ri) ",
                             padding=8, style="Panel.TLabelframe")
        pie.pack(fill="x", pady=(10, 0))
        self.txt = tk.Text(pie, height=3, wrap="word", relief="flat", bg=C["panel"],
                           fg=C["texto"], font=("Consolas", 10), highlightthickness=0)
        self.txt.pack(side="left", fill="x", expand=True)
        ttk.Button(pie, text="Copiar", style="Acento.TButton",
                   command=self._copiar).pack(side="right", padx=(8, 0))

        # Interpretación (lineal y multiplicativo)
        self.lbl_interp = ttk.Label(self, text="", style="Panel.TLabel",
                                    wraplength=880, justify="left")
        self.lbl_interp.pack(anchor="w", fill="x", pady=(10, 0))

        # Ajusta el texto al ancho de la ventana
        self.bind("<Configure>", lambda e: (
            desc.configure(wraplength=max(300, e.width - 60)),
            self.lbl_interp.configure(wraplength=max(300, e.width - 60))))

    def ejecutar(self):
        try:
            n = int(self.n_var.get())
        except ValueError:
            n = 10
        n = max(1, min(1000, n))
        self.n_var.set(str(n))
        self._mostrar(gen.generar(self.clave, n))

    def _mostrar(self, res):
        # Parámetros
        for w in self.marco_params.winfo_children():
            w.destroy()
        for nombre, valor in res.parametros.items():
            caja = ttk.Frame(self.marco_params, style="Panel.TFrame")
            caja.pack(side="left", padx=(0, 26))
            ttk.Label(caja, text=nombre, style="Suave.TLabel").pack(anchor="w")
            ttk.Label(caja, text=str(valor), style="Valor.TLabel").pack(anchor="w")
        self.lbl_notas.configure(text="\n".join("• " + t for t in res.notas))

        # Tabla
        self.tabla.delete(*self.tabla.get_children())
        self.tabla["columns"] = res.columnas
        for i, col in enumerate(res.columnas):
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=60 if i == 0 else 150,
                              stretch=(i != 0))
        for k, fila in enumerate(res.filas):
            self.tabla.insert("", "end", values=fila, tags=("alt",) if k % 2 else ())

        # Lista de números
        self.txt.configure(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", "   ".join(res.numeros))
        self.txt.configure(state="disabled")
        self._numeros = res.numeros

        # Interpretación
        self.lbl_interp.configure(text=res.interpretacion)

    def _copiar(self):
        self.clipboard_clear()
        self.clipboard_append("\n".join(getattr(self, "_numeros", [])))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de números pseudoaleatorios")
        self.geometry("1000x780")
        self.minsize(820, 640)
        self.configure(bg=C["fondo"])
        self._estilos()

        ttk.Label(self, text="Generador de números pseudoaleatorios",
                  style="Cabecera.TLabel").pack(anchor="w", padx=20, pady=(16, 0))
        ttk.Label(self, text="Selecciona un método en las pestañas: los parámetros se eligen "
                             "al azar y el algoritmo se ejecuta automáticamente.",
                  style="Cabecera2.TLabel").pack(anchor="w", padx=20, pady=(0, 10))

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        for clave, info in gen.METODOS.items():
            self.nb.add(PestanaMetodo(self.nb, clave), text=info["pestana"])
        self.nb.bind("<<NotebookTabChanged>>", self._al_cambiar)
        self.after(50, self._al_cambiar)

    def _al_cambiar(self, _evento=None):
        pestana = self.nametowidget(self.nb.select())
        pestana.ejecutar()

    def _estilos(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", font=FUENTE, background=C["panel"], foreground=C["texto"])
        s.configure("Panel.TFrame", background=C["panel"])
        s.configure("Panel.TLabel", background=C["panel"], foreground=C["texto"])
        s.configure("Titulo.TLabel", background=C["panel"], foreground=C["texto"],
                    font=("Segoe UI Semibold", 15))
        s.configure("Suave.TLabel", background=C["panel"], foreground=C["suave"])
        s.configure("Valor.TLabel", background=C["panel"], foreground=C["texto"],
                    font=("Consolas", 12, "bold"))
        s.configure("Cabecera.TLabel", background=C["fondo"], foreground=C["texto"],
                    font=("Segoe UI Semibold", 17))
        s.configure("Cabecera2.TLabel", background=C["fondo"], foreground=C["suave"])
        s.configure("Panel.TLabelframe", background=C["panel"], bordercolor=C["borde"])
        s.configure("Panel.TLabelframe.Label", background=C["panel"], foreground=C["suave"])

        s.configure("TNotebook", background=C["fondo"], borderwidth=0, tabmargins=(0, 0, 0, 0))
        s.configure("TNotebook.Tab", background=C["borde"], foreground=C["suave"],
                    padding=(16, 8), borderwidth=0, font=("Segoe UI", 10))
        s.map("TNotebook.Tab",
              background=[("selected", C["panel"]), ("active", C["seleccion"])],
              foreground=[("selected", C["texto"])])

        s.configure("Acento.TButton", background=C["acento"], foreground="white",
                    padding=(14, 6), borderwidth=0, focusthickness=0)
        s.map("Acento.TButton", background=[("active", C["acento_hover"])])

        s.configure("Treeview", background=C["panel"], fieldbackground=C["panel"],
                    foreground=C["texto"], rowheight=26, bordercolor=C["borde"])
        s.configure("Treeview.Heading", background=C["borde"], foreground=C["texto"],
                    font=("Segoe UI Semibold", 10), padding=6, relief="flat")
        s.map("Treeview", background=[("selected", C["seleccion"])],
              foreground=[("selected", C["texto"])])
        s.configure("TSpinbox", fieldbackground="white", background=C["panel"])