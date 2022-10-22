ARG python_release=3.10

# build the dashboard vite project
FROM node:16 AS dashboard
WORKDIR /src/dashboard

RUN npm install -g npm pnpm
COPY dashboard/pnpm-lock.yaml .
RUN pnpm fetch
COPY dashboard/ ./
RUN pnpm install && pnpm build

FROM python:$python_release AS builder
ENV PIP_NO_CACHE_DIR=no \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_ROOT_USER_ACTION=ignore \
    PDM_USE_VENV=no

RUN pip install pdm

COPY pyproject.toml pdm.lock README.md /project/
COPY /valhalla /project/valhalla
COPY --from=dashboard /src/dashboard/dist /project/valhalla/dashboard/dist

WORKDIR /project
RUN pdm install --prod -G prod --no-lock --no-editable

FROM python:$python_release
ARG python_release
COPY --from=builder /project/__pypackages__ /project/__pypackages__

ENV PATH=$PATH:/project/__pypackages__/$python_release/bin \
    PYTHONPATH=/project/__pypackages__/$python_release/lib

# default port, heroku can override this
ENV PORT=8080
EXPOSE $PORT
CMD gunicorn valhalla:app -k uvicorn.workers.UvicornWorker
