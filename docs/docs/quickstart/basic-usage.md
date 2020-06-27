# Basic Usage

This page describes the basics of creating and running bots. Refer to [this]() page for further details on each of the available Steps.

## Creating a Bot

SeleniumYAML expects each automation guideline to be provided in a particular schema. Each YAML file is treated as an independent bot, and can be passed to the `run_sally` script to be executed.

The base YAML Schema looks like this:

```yaml
title: Bot Title
steps:
    List of steps
```

Each bot should ideally have a unique title (although this is only required if you're chaining bots together using the `run_bot` step), and a list of *steps*.

### Step Schema

Each step defined in the steps array of a Bot file must have a `title` and `action` field, and look similar to the following:

```yaml
title: Step Title
action: Step Identifier
... other fields specific to the step identified by the action
```

The title for each step in the `steps` array must be unique within that bot. This is due to the fact that each step can have it's own namespace within the `performance_context` (defined [here]()).

### Connecting the dots

With the Bot Schema and the Step Schema combined, we can now come up with the basic schema for a bot that performs two steps.

```yaml
title: Bot Title
steps:
  - title: Step 1 Title
    action: Step Identifier
    ... other fields specific to the step
  - title: Step 2 Title
    action: Another Step Identifier
    ... other fields specific to the step
```

## Running a Bot

Bots defined in YAML Files can be run by passing them to the `run_sally` script. The following command would run the bot specified in the `bot.yaml` file:

```bash
run_sally --yaml-file=bot.yaml
```

Use the `--help` flag to get details on other available parameters.

For examples, refer to the bots in [our Github repository](https://github.com/wigeria/selenium-yaml-core).
