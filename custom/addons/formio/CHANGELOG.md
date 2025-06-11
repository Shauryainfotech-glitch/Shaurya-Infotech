# Changelog

## 18.0.1.5

Fixes for public form:
- Fix response for public submission endpoint.
- Fix `_generate_odoo_domain` method for public form.

## 18.0.1.4

Change `formio.form` method `_generate_odoo_domain` to provide the `formio.form` record in args.

## 18.0.1.3

Fix (migration 18) `copy` method in models:
- `formio.builder`
- `ir_actions`
- `ir_attachment`

Since Odoo 18 the `copy` method applies on a multi record set.

## 18.0.1.2

Ensure sufficient formio.js versions (GitHub tags) are downloaded and registered.\
In future versions this will be more configurable.

## 18.0.1.1

Possibility to override the form submit (input) value, by slurping from the input (DOM) element value.\
This is especially useful for external JavaScript (scripts) that modify DOM input elements.

## 18.0.1.0

Initial 18.0 release.
