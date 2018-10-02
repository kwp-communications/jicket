FROM python:3.7

COPY threadtemplate.html /etc/jicket/threadtemplate.html
ENV JICKET_THREAD_TEMPLATE=/etc/jicket/threadtemplate.html

RUN pip install jicket

ENTRYPOINT /usr/local/bin/jicket