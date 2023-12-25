FROM sphinxdoc/sphinx

LABEL image="dunderlab/docs"
LABEL version="1.0"
LABEL maintainer="yencardonaal@unal.edu.co"
LABEL description=""
LABEL project=""
LABEL documentation=""
LABEL license="BSD 2-Clause"

WORKDIR /docs

RUN apt-get update && apt-get install -y pandoc
RUN python3 -m pip install dunderlab-docs \
                           nbsphinx \
                           ipython \
                           'urllib3<2.0' \
                           ipython \
                           ipykernel \
                           nbsphinx \
                           sphinxcontrib-bibtex \
                           pygments
