FROM node:20-alpine

WORKDIR /workspace/mock

COPY mock/package.json ./
COPY mock/server.mjs ./
COPY mock/dist ./dist

EXPOSE 5173

CMD ["npm", "run", "start"]
