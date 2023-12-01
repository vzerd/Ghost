FROM alpine:latest
RUN mkdir /ghost
COPY ./bin/mini-ghost /ghost/
RUN chmod +x /ghost/mini-ghost
WORKDIR /ghost
CMD ["./mini-ghost"]