import tkinter as tk
from tkinter import ttk
import folium
from datetime import datetime
import webbrowser
import tempfile
import os
from typing import List
from Package import Package
from Graph import Graph
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


class DeliveryRoutePlanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Delivery Route Planner")
        self.root.geometry("1200x800")

        self.packages: List[Package] = []
        self.graph = Graph()
        self.geocoder = Nominatim(user_agent="delivery_route_planner")

        self.setup_ui()

    def setup_ui(self):
        # Create main frames
        self.left_frame = ttk.Frame(self.root, padding="10")
        self.right_frame = ttk.Frame(self.root, padding="10")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Package input form
        self.setup_package_form()

        # Package list
        self.setup_package_list()

        # Map view (using folium)
        self.setup_map_view()

        # Route planning controls
        self.setup_route_controls()

    def setup_package_form(self):
        form_frame = ttk.LabelFrame(self.left_frame, text="Add Package", padding="10")
        form_frame.pack(fill=tk.X, pady=5)

        # Address input
        ttk.Label(form_frame, text="Address:").grid(row=0, column=0, sticky=tk.W)
        self.address_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.address_var, width=40).grid(row=0, column=1, padx=5)

        # Priority selection
        ttk.Label(form_frame, text="Priority:").grid(row=1, column=0, sticky=tk.W)
        self.priority_var = tk.IntVar(value=2)
        for i, pri in enumerate(["High", "Medium", "Low"]):
            ttk.Radiobutton(form_frame, text=pri, variable=self.priority_var, value=i + 1).grid(row=1, column=i + 1)

        # Add button
        ttk.Button(form_frame, text="Add Package", command=self.add_package).grid(row=2, column=1, pady=10)

    def setup_package_list(self):
        list_frame = ttk.LabelFrame(self.left_frame, text="Package List", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ("ID", "Address", "Priority", "Status")
        self.package_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        for col in columns:
            self.package_tree.heading(col, text=col)
            self.package_tree.column(col, width=100)

        self.package_tree.pack(fill=tk.BOTH, expand=True)

    def setup_map_view(self):
        self.map_frame = ttk.LabelFrame(self.right_frame, text="Route Map", padding="10")
        self.map_frame.pack(fill=tk.BOTH, expand=True)

        # Initial map creation
        self.update_map()

    def setup_route_controls(self):
        control_frame = ttk.Frame(self.right_frame, padding="10")
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Button(control_frame, text="Calculate Route", command=self.calculate_route).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)

    def add_package(self):
        address = self.address_var.get()
        if not address:
            return

        # Geocode address
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
            tk.messagebox.showerror("Error", f"Error adding package: {str(e)}")

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
        if not self.packages:
            center = [0, 0]
        else:
            center = [self.packages[0].latitude, self.packages[0].longitude]

        m = folium.Map(location=center, zoom_start=13)

        # Add markers for all packages
        for pkg in self.packages:
            folium.Marker(
                [pkg.latitude, pkg.longitude],
                popup=f"ID: {pkg.id}\nPriority: {pkg.priority}",
                icon=folium.Icon(color='red' if pkg.priority == 1 else 'blue')
            ).add_to(m)

        # Draw route if available
        if route:
            coordinates = [(pkg.latitude, pkg.longitude) for pkg in route]
            folium.PolyLine(coordinates, weight=2, color='red').add_to(m)

        # Save map to temporary file and display
        _, temp_path = tempfile.mkstemp(suffix='.html')
        m.save(temp_path)
        webbrowser.open(f'file://{temp_path}')

    def calculate_route(self):
        if len(self.packages) < 2:
            return

        # Create graph
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

        # Calculate optimal route
        start_pkg = self.packages[0]
        route = []
        current_pkg = start_pkg
        unvisited = set(pkg.id for pkg in self.packages[1:])

        while unvisited:
            _, path = min(
                (self.graph.get_shortest_path(current_pkg.id, pkg_id) for pkg_id in unvisited),
                key=lambda x: x[1]
            )
            next_pkg_id = path[1] if len(path) > 1 else path[0]
            next_pkg = next(pkg for pkg in self.packages if pkg.id == next_pkg_id)
            route.append(next_pkg)
            unvisited.remove(next_pkg_id)
            current_pkg = next_pkg

        # Update map with route
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
