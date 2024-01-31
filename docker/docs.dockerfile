FROM sphinxdoc/sphinx

LABEL image="dunderlab/docs"
LABEL version="1.3"
LABEL maintainer="yencardonaal@unal.edu.co"
LABEL description=""
LABEL project=""
LABEL documentation=""
LABEL license="BSD 2-Clause"

WORKDIR /mnt

RUN apt-get update && apt-get install -y pandoc
RUN python3 -m pip install 'dunderlab-docs>=0.24' \
                           nbsphinx \
                           ipython \
                           'urllib3<2.0' \
                           ipython \
                           ipykernel \
                           sphinxcontrib-bibtex \
                           pygments
