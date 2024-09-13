"""
File with the class for manipulating gromacs
"""
import logging
from pathlib import Path
import tarfile
import re
import shutil
import docker

from helpers import find_files_with_same_pattern, create_folder

logging.basicConfig(
    format='[%(asctime)s] - %(levelname)s - %(filename)s - %(funcName)s:%(lineno)d - %(message)s',
    level=logging.INFO
)


class GromacsData:
    """
    Class for creating all the necessary data for the gromacs analysis.
    """
    CONTAINER_WORK_DIR = "/container/data"

    def __init__(self, path: Path) -> None:
        self.path: Path = Path(path)
        self.volume: dict = {
            self.path: {
                'bind': self.CONTAINER_WORK_DIR,
                'mode': 'rw'
            }
        }

        create_folder(self.path)
        self.results_folder: Path = Path(f"{self.path}/results")

    def _run_gromacs_container(
        self,
        command,
        working_dir=CONTAINER_WORK_DIR,
        **kwargs
    ):
        """
        Run the Gromacs container with the specified command and arguments.
        """
        gromacs_image = "jpmontoya19/gromacs:latest"
        client = docker.from_env()
        return client.containers.run(
            gromacs_image,
            command,
            working_dir=working_dir,
            **kwargs
        )

    def _find_last_tpr_file(self) -> Path:
        """
        Finds the last TPR file in the given path.

        Returns:
            A tuple containing the name and path of the last TPR file.
        """
        last_tpr = find_files_with_same_pattern(self.path, "md_0_*.tpr")[-1]
        return (last_tpr.name, last_tpr)

    def generate_minimization_data(self):
        """
        Generates energy minimization data using GROMACS.

        Returns:
            str: The output of the energy minimization process.
        """
        command = [
            "sh",
            "-c",
            "echo 10 0 | gmx energy -f em.edr -o potential.xvg"
        ]

        logging.info(command[-1])
        energy_minimization = self._run_gromacs_container(
            command,
            volumes=self.volume,
            remove=True
        ).decode("utf-8")

        return energy_minimization

    def generate_nvt_data(self):
        """
        Generates NVT data using GROMACS.

        Returns:
            str: The temperature data as a string.
        """
        command = [
            "sh",
            "-c",
            "echo 16 0 | gmx energy -f nvt.edr -o temperature.xvg"
        ]

        logging.info(command[-1])
        temperature = self._run_gromacs_container(
            command,
            volumes=self.volume
        ).decode("utf-8")
        return temperature

    def generate_npt_data(self):
        """
        Generates pressure and density data using GROMACS.

        Returns:
            str: A string containing the pressure and density data, separated by a comma.
        """
        command_pressure = [
            "sh",
            "-c",
            "echo 18 0 | gmx energy -f npt.edr -o pressure.xvg"
        ]

        logging.info(command_pressure[-1])
        pressure = self._run_gromacs_container(
            command_pressure,
            volumes=self.volume
        ).decode("utf-8")

        command_density = [
            "sh",
            "-c",
            "echo 24 0 | gmx energy -f npt.edr -o density.xvg"
        ]

        logging.info(command_density[-1])
        density = self._run_gromacs_container(
            command_density,
            volumes=self.volume
        ).decode("utf-8")

        return f"{pressure}, \n, {density}"

    def generate_final_xtc_file(self):
        """
        Generates the final .xtc file by extracting .xtc files from tar.gz files and
        concatenating them using GROMACS.

        Returns:
            None
        """
        steps = find_files_with_same_pattern(
            self.path, "my_job_*.output.tar.gz")

        xtc_files = []
        for step in steps:
            with tarfile.open(step, "r:gz") as tar:
                for member in tar.getmembers():
                    if member.name.endswith(".xtc"):
                        tar.extract(member, path=f"{self.path}")
                        xtc_files.append(member.name)

        command = [
            "sh",
            "-c",
            f"gmx trjcat -f {' '.join(xtc_files)} -o final.xtc"
        ]

        logging.info(command[-1])
        _ = self._run_gromacs_container(
            command,
            volumes=self.volume
        )

        shutil.rmtree(f"{self.path}/my_output")

    def fix_periodicity(self):
        """
        Fixes the periodicity of the trajectory by centering the molecules and
        applying periodic boundary conditions.

        Returns:
            str: The output of the GROMACS command for fixing periodicity.
        """
        filename, _ = self._find_last_tpr_file()
        command = [
            "sh",
            "-c",
            f"echo 1 0 | gmx trjconv -s {
                filename} -f final.xtc -o fixed.xtc -center -pbc mol -ur compact"  # pylint: disable=line-too-long
        ]

        logging.info(command[-1])
        periodicity = self._run_gromacs_container(
            command,
            volumes=self.volume
        ).decode("utf-8")

        return periodicity

    def get_initial_configuration(self):
        filename, _ = self._find_last_tpr_file()

        command = [
            "sh",
            "-c",
            f"""
                echo 22 | \
                gmx trjconv \
                    -s {filename} \
                    -f fixed.xtc \
                    -n index.ndx \
                    -o initial_configuration.pdb \
                    -dump 0
            """
        ]

        logging.info(command[-1])

        _ = self._run_gromacs_container(
            command,
            volumes=self.volume
        )

    def get_latest_configuration(self):
        """
        Retrieves the latest configuration from the trajectory file.

        Returns:
            None
        """
        command = [
            "sh",
            "-c",
            "gmx check -f fixed.xtc > trajectory_info.txt 2>&1"
        ]

        _ = self._run_gromacs_container(
            command,
            volumes=self.volume
        )

        with open(f"{self.path}/trajectory_info.txt", "r", encoding='utf-8') as file:
            lines = file.readlines()

        last_frame = None
        for line in lines:
            match = re.search(r'Last frame\s+(\d+(\.\d+)?)', line)

            if match:
                last_frame = match.group(1)
                break

        logging.info("Last frame: %s", last_frame)

        filename, _ = self._find_last_tpr_file()

        command = [
            "sh",
            "-c",
            f"""
                echo 22 | \
                gmx trjconv \
                    -s {filename} \
                    -f fixed.xtc \
                    -n index.ndx \
                    -o last_configuration.pdb \
                    -dump {last_frame}
            """
        ]

        logging.info(command[-1])
        _ = self._run_gromacs_container(
            command,
            volumes=self.volume
        )
