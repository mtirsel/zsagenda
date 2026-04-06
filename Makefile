SSH_HOST   = ctsrv
SSH_USER   = root
APP_USER   = zsagenda
APP_DIR    = /srv/apps/zsagenda/src
PROJECT    = zsagenda

DOWN := $(filter down,$(MAKECMDGOALS))

.PHONY: deploy down

deploy:
	@echo "==> Checking for uncommitted changes..."
	@git diff --quiet && git diff --cached --quiet || (echo "ERROR: Working tree is not clean. Commit or stash your changes first." && exit 1)
	@echo "==> Checking that all commits are pushed..."
	@test "$$(git rev-parse HEAD)" = "$$(git rev-parse @{u})" || (echo "ERROR: Local commits not pushed to remote." && exit 1)
	@echo "==> Pulling latest code on server as $(APP_USER)..."
	ssh $(SSH_USER)@$(SSH_HOST) su - $(APP_USER) -c "'cd $(APP_DIR) && git pull'"
	@echo "==> Building images on server..."
	ssh $(SSH_USER)@$(SSH_HOST) "cd $(APP_DIR) && docker compose -p $(PROJECT) build"
ifdef DOWN
	@echo "==> Stopping containers on server..."
	ssh $(SSH_USER)@$(SSH_HOST) "cd $(APP_DIR) && docker compose -p $(PROJECT) down"
endif
	@echo "==> Starting containers on server..."
	ssh $(SSH_USER)@$(SSH_HOST) "cd $(APP_DIR) && docker compose -p $(PROJECT) up -d"
	@echo "==> Collecting static files..."
	ssh $(SSH_USER)@$(SSH_HOST) "cd $(APP_DIR) && docker compose -p $(PROJECT) exec app uv run python manage.py collectstatic --noinput"
	@echo "==> Deploy complete."

down:
	@true
