"""
File with the class for plotting the data
"""

import logging
from pathlib import Path
from matplotlib import pyplot as plt

from helpers import create_folder, read_xvg_files


logging.basicConfig(
    format='[%(asctime)s] - %(levelname)s - %(filename)s - %(funcName)s:%(lineno)d - %(message)s',
    level=logging.INFO
)


class Plots:

    def __init__(self, path: Path, protein: str) -> None:
        self.path: Path = path
        self.protein: str = protein

        self.images_path = f"{self.path}/images/"
        create_folder(self.path, "images")

    def plot_data(self, x, y, titles):
        """
        Plot the given data.

        Args:
            x (list): The x-coordinates of the data points.
            y (list): The y-coordinates of the data points.
            titles (list): A list of titles for the plot, where titles[0] is the x-axis label,
                           titles[1] is the y-axis label, and titles[2] is the plot title.
                           If titles has a length of 4, titles[-1] is used as the legend.

        Returns:
            matplotlib.figure.Figure: The generated figure object.
        """
        fig, ax = plt.subplots()

        ax.plot(x, y, color='black', linewidth=0.7)

        # Add labels and title
        plt.xlabel(titles[0])
        plt.ylabel(titles[1])
        plt.title(titles[2])

        if len(titles) == 4:
            plt.legend(titles[-1])

        plt.xlim(left=x[0], right=x[-1])

        plt.minorticks_on()

        plt.tick_params(axis='both', which='both',
                        direction='in', right=True, top=True)

        return fig

    def plot_energy_minimization(self):
        """
        Plots the energy minimization data.

        Reads the energy data from the potential.xvg file and plots it.
        The x-axis represents time in nanoseconds, and the y-axis represents
        potential energy in kJ/mol.

        Returns:
            None
        """
        energy_data = read_xvg_files(f"{self.path}/potential.xvg")

        _ = self.plot_data(
            energy_data[:, 0]/1000,
            energy_data[:, 1],
            [
                'Time $(ns)$',
                'Potential Energy $(kJ/mol)$',
                self.protein
            ]
        )

        plt.suptitle('Energy Minimization', fontsize=20, y=1)

        plt.savefig(
            self.images_path + "minimization.png",
            bbox_inches='tight',
            pad_inches=0.1,
            dpi=300
        )

    def plot_temperature(self):
        """
        Plots the temperature data from the temperature.xvg file.

        Reads the temperature data from the temperature.xvg file located in the specified path.
        Plots the temperature data against time and potential energy.
        Saves the plot as a PNG image file.

        Returns:
            None
        """
        temperature = read_xvg_files(f"{self.path}/temperature.xvg")

        _ = self.plot_data(
            temperature[:, 0],
            temperature[:, 1],
            [
                'Time $(ps)$',
                'Potential Energy $(K)$',
                f"{self.protein}, NVT Equilibration"
            ]
        )

        plt.suptitle('Temperature', fontsize=20, y=1)

        plt.savefig(
            self.images_path + "temperature.png",
            bbox_inches='tight',
            pad_inches=0.1,
            dpi=300
        )

    def plot_pressure(self):
        """
        Plots the pressure data from the pressure.xvg file.

        Returns:
            None
        """
        pressure = read_xvg_files(f"{self.path}/pressure.xvg")

        _ = self.plot_data(
            pressure[:, 0],
            pressure[:, 1],
            [
                'Time $(ps)$',
                'Pressure $(bar)$',
                f"{self.protein}, NPT Equilibration"
            ]
        )

        plt.suptitle('Pressure', fontsize=20, y=1)

        plt.savefig(
            self.images_path + "pressure.png",
            bbox_inches='tight',
            pad_inches=0.1,
            dpi=300
        )

    def plot_density(self):
        """
        Plots the density data from the density.xvg file.

        Returns:
            None
        """
        density = read_xvg_files(f"{self.path}/density.xvg")

        _ = self.plot_data(
            density[:, 0],
            density[:, 1],
            [
                'Time $(ps)$',
                'Density $(kg/m^{3})$',
                f"{self.protein}, NPT Equilibration"
            ]
        )

        plt.suptitle('Density', fontsize=20, y=1)

        plt.savefig(
            self.images_path + "density.png",
            bbox_inches='tight',
            pad_inches=0.1,
            dpi=300
        )
