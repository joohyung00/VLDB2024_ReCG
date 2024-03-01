
<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D




<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- [![Contributors][contributors-shield]][contributors-url] -->
<!-- [![Forks][forks-shield]][forks-url] -->
<!-- [![Stargazers][stars-shield]][stars-url] -->
<!-- [![Issues][issues-shield]][issues-url] -->
<!-- [![MIT License][license-shield]][license-url] -->
<!-- [![LinkedIn][linkedin-shield]][linkedin-url] -->



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <!-- <a href="https://github.com/github_username/repo_name">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a> -->

<h3 align = "center">ReCG: Bottom-Up JSON Schema Discovery Using a Repetitive Cluster-and-Generalize Framework</h3>

  <p align = "center">
    ReCG is the first bottom-up JSON schema discovery algorithm.
    <!-- <br />
    <a href="https://github.com/github_username/repo_name"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/github_username/repo_name">View Demo</a>
    ·
    <a href="https://github.com/github_username/repo_name/issues">Report Bug</a>
    ·
    <a href="https://github.com/github_username/repo_name/issues">Request Feature</a> -->
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-recg">About ReCG</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#download-docker-image">Download Docker Image</a></li>
        <li><a href="#create-docker-container">Create Docker Container</a></li>
      </ul>
    </li>
    <li><a href="#quick-reproduction">Quick Reproduction</a></li>
    <li><a href="#explanation-about-directories">Explanation About Directories</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About ReCG

`ReCG` is an algorithm that discovers a JSON schema from a bag of JSON documents.

`ReCG` processes JSON documents in a bottom-up manner, which is devised to solve the problems top-down algorithms that perform poorly in real-life datasets.
It builds up schemas from leaf elements upward in the JSON document tree and, thus, can make more informed decisions of the schema node types.

In addition, `ReCG` adopts MDL (Minimum Description Length) principles systematically while building up the schemas to choose among candidate schemas the most concise yet accurate one with well-balanced generality.

`ReCG` is implemented with ![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- 
### Built With

* [![Next][Next.js]][Next-url]
* [![React][React.js]][React-url]
* [![Vue][Vue.js]][Vue-url]
* [![Angular][Angular.io]][Angular-url]
* [![Svelte][Svelte.dev]][Svelte-url]
* [![Laravel][Laravel.com]][Laravel-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![JQuery][JQuery.com]][JQuery-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p> -->

<!-- GETTING STARTED -->

## Getting Started

This page guides you to reproduce the results written in the paper "ReCG: Bottom-Up JSON Schema Discovery Using a Repetitive Cluster-and-Generalize Framework".

Please refer to the instructions below.



### Prerequisites

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

You must be able to download our docker image from the docker cloud.
Please refer to [Docker Docs](https://docs.docker.com) to download docker.

### Download Docker Image

We made a docker image of our environment.
Please download from docker cloud.

1. Download our image from docker cloud
    ```bash
    docker pull joohyungyun/recg-vldb-2024-3:1.0
    ```

### Create Docker Container

Create a docker container named `recg-image` (this may change!) using the downloaded image.

1. Docker run
    ```bash
    docker run -itd --name recg-vldb-2024-3 joohyungyun/recg-vldb-2024-3:1.0 /bin/bash
    ```
2. Docker start
    ```bash
    docker start recg-vldb-2024-3
    ```
3. Docker init
    ```bash
    docker init recg-vldb-2024-3
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Quick Reproduction

The whole reproduction process can be easily done by typing a single line

```bash
./runAll.sh
```

The anticipated runtime of the whole process is over 4 full days, so we recomment you to run the process using `tmux`!

For detailed explanation or for a more fine-grained run, jump to <a href="#usage">Usage</a>


## Explanation about Directories

- ReCG

This directory contains the `C++` implementation of `ReCG`.
Refer to `README.md` of this directory for more information.

- Dataset

This directory contains all 20 datasets used in the paper "ReCG: Bottom-Up JSON Schema Discovery Using a Repetitive Cluster-and-Generalize Framework".

- Experiment

This directory contains the `Python` implementations for the four experiments conducted in "ReCG: Bottom-Up JSON Schema Discovery Using a Repetitive Cluster-and-Generalize Framework".
Refer to `README.md` of this directory for more information.

- ExperimentVisualization

This directory contains the `Python` implementations that visualize (either printing in consoles or drawing plots) experiments conducted in "ReCG: Bottom-Up JSON Schema Discovery Using a Repetitive Cluster-and-Generalize Framework".
Refer to `README.md` of this directory for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Usage

Please follow the instructions below to 

### 1. Build Algorithms

(a) Build ReCG
```bash
cd ReCG
./make.sh
cd ..
```

(b) Build Jxplain

```bash
./buildJxplain.sh
```

(c) Build KReduce
```bash
./buildKReduce.sh
```

### 2. Run Experiments

Run all experiments and return to this directory.
```bash
cd Experiment
./runAllExperiments.sh
cd ..
```

For detailed explanation of each experiments, refer `README.md` of `Experiements` directory.

### 3. Visualize Experiment Results

Run all experiments visualizations and return to this directory.
```bash
cd ExperimentVisualization
./runAllExperimentVisualizations.sh
cd ..
```

For detailed explanation of each experiments, refer `README.md` of `ExperiementVisualizations` directory.


<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Joohyung Yun - jhyun@dblab.postech.ac.kr

Byunchul Tak - bctak@knu.ac.kr

Wook-Shin Han - wshan@dblab.postech.ac.kr


<p align="right">(<a href="#readme-top">back to top</a>)</p>

