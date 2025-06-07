import tkinter as tk
from tkinter import ttk, messagebox
import folium
import webbrowser
import tempfile
from typing import List
from Packpage import Package
from Graph import Graph
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Clase principal para la planificación de rutas de entrega
class DeliveryRoutePlanner:
    def __init__(self):
        # Inicializa la ventana principal de la aplicación
        self.root = tk.Tk()
        self.root.title("🚚 Delivery Route Planner")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f4f7")  # Fondo suave

        # Lista de paquetes a entregar
        self.packages: List[Package] = []
        # Grafo para calcular rutas
        self.graph = Graph()
        # Geocodificador para convertir direcciones en coordenadas
        self.geocoder = Nominatim(user_agent="delivery_route_planner")

        # Configuración de estilos para la interfaz
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Segoe UI", 12))
        self.style.configure("TButton", font=("Segoe UI", 11), padding=6)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

        # Llama al método para construir la interfaz de usuario
        self.setup_ui()

    def setup_ui(self):
        # Crea los marcos principales con color de borde
        self.left_frame = tk.Frame(self.root, bg="#ffffff", highlightbackground="#3498db", highlightthickness=3)
        self.right_frame = tk.Frame(self.root, bg="#ffffff", highlightbackground="#2ecc71", highlightthickness=3)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.setup_package_form()
        self.setup_package_list()
        self.setup_map_view()
        self.setup_route_controls()

    def setup_package_form(self):
        form_frame = ttk.LabelFrame(self.left_frame, text="➕ Add Package", padding="10")
        form_frame.pack(fill=tk.X, pady=5)

        ttk.Label(form_frame, text="Address:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.address_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.address_var, width=40).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Priority:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.priority_var = tk.IntVar(value=2)
        for i, pri in enumerate(["High", "Medium", "Low"]):
            ttk.Radiobutton(form_frame, text=pri, variable=self.priority_var, value=i + 1).grid(row=1, column=i + 1, pady=5)

        ttk.Button(form_frame, text="Add Package", command=self.add_package).grid(row=2, column=1, pady=10)

    def setup_package_list(self):
        list_frame = ttk.LabelFrame(self.left_frame, text="📦 Package List", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ("ID", "Address", "Priority", "Status")
        self.package_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        for col in columns:
            self.package_tree.heading(col, text=col)
            self.package_tree.column(col, width=120)

        self.package_tree.pack(fill=tk.BOTH, expand=True)

    def setup_map_view(self):
        self.map_frame = ttk.LabelFrame(self.right_frame, text="🗺️ Route Map", padding="10")
        self.map_frame.pack(fill=tk.BOTH, expand=True)

        self.update_map()

    def setup_route_controls(self):
        control_frame = ttk.Frame(self.right_frame, padding="10")
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Button(control_frame, text="🚗 Calculate Route", command=self.calculate_route).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🗑️ Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)

    def add_package(self):
        address = self.address_var.get()
        if not address:
            return

        try:
            location = self.geocoder.geocode(address)
            if location is None:
                raise ValueError("Address not found")

            package = Package(
                id=f"PKG{len(self.packages) + 1}",
                address=address,
                latitude=location.latitude,
                longitude=location.longitude,
                priority=self.priority_var.get()
            )

            self.packages.append(package)
            self.update_package_list()
            self.update_map()
            self.address_var.set("")

        except Exception as e:
            messagebox.showerror("Error", f"Error adding package: {str(e)}")

    def update_package_list(self):
        for item in self.package_tree.get_children():
            self.package_tree.delete(item)

        for pkg in self.packages:
            self.package_tree.insert("", tk.END, values=(
                pkg.id,
                pkg.address,
                ["High", "Medium", "Low"][pkg.priority - 1],
                pkg.status
            ))

    def update_map(self, route=None):
        # Si hay una ruta, centra el mapa en el primer punto de la ruta
        if route and len(route) > 0:
            center = [route[0].latitude, route[0].longitude]
        elif self.packages:
            center = [self.packages[0].latitude, self.packages[0].longitude]
        else:
            center = [0, 0]

        m = folium.Map(location=center, zoom_start=13)

        for pkg in self.packages:
            folium.Marker(
                [pkg.latitude, pkg.longitude],
                popup=f"ID: {pkg.id}\nPriority: {pkg.priority}",
                icon=folium.Icon(color='red' if pkg.priority == 1 else 'blue')
            ).add_to(m)

        if route:
            coordinates = [(pkg.latitude, pkg.longitude) for pkg in route]
            folium.PolyLine(coordinates, weight=4, color='red').add_to(m)

        _, temp_path = tempfile.mkstemp(suffix='.html')
        m.save(temp_path)
        webbrowser.open(f'file://{temp_path}')

    def calculate_route(self):
        if len(self.packages) < 2:
            messagebox.showinfo("Info", "Add at least two packages to calculate a route.")
            return

        # Recreate the graph
        self.graph = Graph()

        # Add edges between all packages
        for i, pkg1 in enumerate(self.packages):
            for j, pkg2 in enumerate(self.packages):
                if i != j:
                    distance = geodesic(
                        (pkg1.latitude, pkg1.longitude),
                        (pkg2.latitude, pkg2.longitude)
                    ).kilometers
                    self.graph.add_edge(pkg1.id, pkg2.id, distance)

        start_pkg = self.packages[0]
        route = [start_pkg]
        current_pkg = start_pkg
        unvisited = set(pkg.id for pkg in self.packages[1:])

        while unvisited:
            nearest_pkg = None
            nearest_distance = float('inf')

            # Manually find nearest unvisited neighbor
            for pkg_id in unvisited:
                path = self.graph.get_shortest_path(current_pkg.id, pkg_id)
                if not path or len(path) < 2:
                    continue
                next_pkg_id = path[1]  # Next hop in the path
                next_pkg = next(pkg for pkg in self.packages if pkg.id == pkg_id)

                # Calculate actual geodesic distance to this node
                distance = geodesic(
                    (current_pkg.latitude, current_pkg.longitude),
                    (next_pkg.latitude, next_pkg.longitude)
                ).kilometers

                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_pkg = next_pkg

            if nearest_pkg is None:
                break  # No reachable unvisited packages

            route.append(nearest_pkg)
            unvisited.remove(nearest_pkg.id)
            current_pkg = nearest_pkg

        self.update_map(route)

    def clear_all(self):
        self.packages.clear()
        self.update_package_list()
        self.update_map()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DeliveryRoutePlanner()
    app.run()
