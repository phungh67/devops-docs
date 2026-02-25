FROM node:20.12 as builder
WORKDIR /app

ADD . ./
RUN npm install

FROM node:20.12
WORKDIR /app

COPY --from=builder /app /app

CMD ["npm", "run", "dev", "--", "--host"]
