# Software Reliability Analysis

A practical implementation and comparison of classical software reliability models using Python.

This project implements three software reliability models:

- Jelinski-Moranda
- Schuman
- Nelson-Corcoran

The models are used to estimate software reliability, failure intensity, and Mean Time To Failure (MTTF).
The calculations are also integrated into the Flask-based VulnMart application through a REST API endpoint.

---

## Project Objectives

The main goals of this project are:

- Study classical mathematical software reliability models
- Perform reliability calculations using Python
- Compare different reliability estimation approaches
- Generate reliability curves
- Integrate reliability calculations into a Flask application
- Provide reliability results through a JSON API

---

## Implemented Reliability Models

### 1. Jelinski-Moranda Model

The Jelinski-Moranda model assumes that the failure intensity is proportional to the number of remaining faults.

Failure intensity:

text
λ(i) = φ × (N0 - i)


Reliability:

text
R(t) = exp(-λt)


For the practical dataset:

text
R(100) = 0.8187
MTTF = 500 hours


---

### 2. Schuman Model

The Schuman model uses residual fault density per machine instruction.

Residual fault density:

text
εr = (E0 - Ec) / I


Failure intensity:

text
λ = Ks × εr


Reliability:

text
R(t) = exp(-λt)


For the practical dataset:

text
R(100) = 0.99998
MTTF = 5,000,000 hours


---

### 3. Nelson-Corcoran Model

The Nelson-Corcoran model is a static software reliability model based on test execution results.

Nelson reliability estimate:

text
R = 1 - Σ (ni / Ni) × Pi


Calculated results:

text
Nelson:     R = 0.9540
Corcoran:   R = 0.9860
Simplified: R = 0.9700


---

## Results

| Model | Reliability | MTTF |
|---|---:|---:|
| Jelinski-Moranda | 0.8187 | 500 hours |
| Schuman | 0.99998 | 5,000,000 hours |
| Nelson-Corcoran | 0.954 - 0.986 | N/A |

The Jelinski-Moranda model provides the most conservative estimate.

The Schuman model provides the most optimistic estimate.

The Nelson-Corcoran model provides an intermediate estimate based on test runs and input distribution.

---

## Reliability Plot

The project generates:

text
reliability_curves.png


The graph compares the Jelinski-Moranda and Schuman models over operating time.

Target reliability level:

text
R = 0.95


---

## Flask Integration

The reliability models are integrated into the VulnMart Flask application.

Start the application:

bash
cd vulnmart
python app.py


The application runs on:

text
http://127.0.0.1:5055


---

## Reliability API

The application provides:

text
GET /reliability


Example request:

bash
curl "http://127.0.0.1:5055/reliabilityt=100&i=30&Ec=30"


Example response:

json
{
  "corrected_errors": 30,
  "jelinski_moranda": {
    "MTTF": 500.0,
    "R": 0.8187,
    "lambda": 0.002
  },
  "nelson_corcoran": {
    "R_corcoran": 0.986,
    "R_nelson": 0.954,
    "R_simple": 0.97
  },
  "schuman": {
    "MTTF": 5000000.0,
    "R": 0.99998,
    "lambda": 2e-07
  },
  "time_hours": 100.0
}


---

## Project Structure

text
software-reliability-analysis/
 src/
    reliability_models.py
 vulnmart/
    app.py
    reliability_models.py
    requirements.txt
    templates/
 reliability_curves.png
 README.md
 .gitignore


---

## Technologies

- Python
- Flask
- NumPy
- Matplotlib
- Git
- GitHub

---

## Conclusion

Different software reliability models produce different estimates because they use different assumptions and input data.

The Jelinski-Moranda model gives the most conservative result, while the Schuman model gives the most optimistic result.

The Nelson-Corcoran model provides a practical estimate based on test execution data.

This project demonstrates software reliability modeling, mathematical analysis, visualization, and integration into a Flask application.
