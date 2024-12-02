FROM continuumio/miniconda3:24.7.1-0

# Copy project files
COPY environment.yml /home/environment.yml

# Create a Conda environment with JupyterLab installed
RUN conda env create -f /home/environment.yml

# Activate the Conda environment
RUN echo "conda activate ndvi-lst" >> ~/.bashrc
ENV PATH="$PATH:/opt/conda/envs/ndvi-lst/bin"

# Create a non-root user and switch to that user
RUN useradd -m assignment
USER assignment

# Set the working directory to /home/assignment
WORKDIR /home/assignment

# Expose the JupyterLab port
EXPOSE 8888

# Expose the Dask Dashboard port
EXPOSE 8787

# Start JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0"]
