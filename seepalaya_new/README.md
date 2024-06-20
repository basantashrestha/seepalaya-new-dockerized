# Seepalaya

Seepalaya is an interactive self-learning app that offers various courses for learners of different levels. It provides an engaging and personalized way to learn through curated content including interactive digital activities, videos, quizzes, slide presentations and games. The app is suitable for learners who prefer to study on their own, at home or with guidance from a parent, guardian or teacher. It covers a variety of topics and aims to enhance knowledge while keeping learning fun.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Node.js (version 8.0 or later)
- npm (Node Package Manager, comes with Node.js)
- yarn (The package manager used to create this application, can use npm, but it is advised to not mix package managers )

### Installing the Application

**1. Clone or download the repository to your local machine**

```bash
git clone https://git2023.olenepal.org/bishal.pokharel/seepalaya_new.git
```

**2. Navigate to the project directory**

```bash
cd seepalaya_new
```

**3. Install the required dependencies**

```bash
npm install
```

### Running the application

**1. Start the development server**

```bash
npm start
```

**2. The app should automatically open in a browser, if it doesn't:**

Open http://localhost:3000 in your web browser to view the debug build of your application.

_Any changes made to the code will reflect on the web browser._

_Guide for running this application without breaking anything can be found [here](#start-guide)_

### Building the Application

**1. Build the application for production**

```bash
npm build
```

## Built with

- [next](https://nextjs.org/) - The React framework for production.
- [react](https://reactjs.org/) - A JavaScript library for building user interfaces.
- [react-dom](https://reactjs.org/docs/react-dom.html) - Serves as the entry point to the DOM and server renderers for React.
- [@reduxjs/toolkit](https://redux-toolkit.js.org/) - The toolkit used for efficient Redux development.
- [axios](https://axios-http.com/) - A promise-based HTTP client for making requests.
- [formik](https://formik.org/) - A library for building forms in React.
- [lucide-react](https://lucide.dev/docs/lucide-react) - Icon toolkit for React.
- [papaparse](https://www.papaparse.com/) - A powerful CSV parser for JavaScript.
- [react-intl](https://formatjs.io/docs/react-intl) - React components and an API for internationalization.
- [react-redux](https://react-redux.js.org/) - Official React bindings for Redux.
- [yup](https://github.com/jquense/yup) - A JavaScript schema builder for value parsing and validation.


## Authors

- **Nabin Khadka** - [Gitlab OLE](https://git.olenepal.org/nabin.khadka)
- **Basanta Shrestha** - [Gitlab OLE](https://git.olenepal.org/basanta.shrestha)

## File Structure

- **.next/**

  - Contains the build output for the Next.js application.

- **app/**

  - Directory for application-specific files.

- **components/**

  - Contains all the reusable components used throughout the application.

- **lib/redux/**

  - **features/classroom/** - redux slice for classroom specific features

  - `store.ts` - Configuration for the Redux store.
  - `StoreProvider.tsx` - Provider component for the Redux store.

- **node_modules/**

  - Contains all the Node.js packages installed via npm or yarn.

- **public/**

  - Contains all the files accessible publicly through the website URL (http://localhost:3000/{filename.fileExtension}).

- **.env**

  - Environment variables file.

- **.env.example**

  - Example environment variables file.

- **.eslintrc.json**

  - Configuration file for ESLint.

- **.gitignore**

  - Specifies files and directories that Git should ignore.

- **next-env.d.ts**

  - TypeScript definitions for Next.js.

- **next.config.mjs**

  - Configuration file for Next.js.

- **package-lock.json**

  - Automatically generated file that contains the exact versions of dependencies and their dependencies.

- **package.json**

  - Contains all the packages, dev dependencies, and scripts for the application.

- **postcss.config.mjs**

  - Configuration file for PostCSS.

- **README.md**

  - Contains information about the project.

- **tailwind.config.ts**

  - Configuration file for Tailwind CSS.

- **tsconfig.json**

  - Configuration file for TypeScript.


## Main Branches

- **refactor**

  - This is essentially the `dev` branch for this project
  - Updates are pushed here and tested before merging to the master branch

- **master**
  - This is the `main` / `master` branch
  - Final updates are pushed here


## Start Guide

If you haven't yet cloned the project, start [here](#installing-the-application)

Start working on the project without affecting the main branches

### To create a new branch

```bash
git checkout -b your-branch-name
```

### To push the branch to remote git server

```bash
git push -u origin your-branch-name
```

### To merge changes to `refactor` branch

**1. First checkout to refactor branch**

```bash
git checkout refactor
```

**2. Merge changes from your branch**

```bash
git merge your-branch-name
```

**3. Push changes**

```bash
git push
```

**4. Checkout back to your branch**

```bash
git checkout your-branch-name
```

### To switch to a different branch

```bash
git checkout branch-name
```

### To merge to the master branch

**1. First checkout to master branch**

```bash
git checkout master
```

**2. Merge changes from your branch**

```bash
git merge your-branch-name
```

**3. Push changes**

```bash
git push
```

**4. Checkout back to your branch**

```bash
git checkout your-branch-name
```
