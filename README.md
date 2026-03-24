# PVPHS-ROV

## Study

1. github
   1. read document
   2. create issue
1. linux (ubuntu)
1. docker
1. blueos
1. uv
1. git

## frontend

how to create frontend website

```sh
# nvm install
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.zshrc
# nvm - node install
nvm install --lts

# confirm
node -v
npm -v
```

```sh
npx create-next-app@latest . --typescript --tailwind --eslint --src-dir --app --import-alias "@/*"

# yes

✔ Would you like to use React Compiler? => Yes
✔ Would you like to include AGENTS.md to guide coding agents to write up-to-date Next.js code? => Yes
```

## deploy to raspberry pi

```sh
mkdir -p /data/git
cd /data/git
git clone git@github.com:MasonKim000/PVPHS-ROV.git
cd PVPHS-ROV/frontend

# install shadcn ui

npx shadcn@latest init --defaults
npx shadcn@latest add card progress

npm ci

npm run dev
```

### let's check

http://192.168.254.245:3000

it works
