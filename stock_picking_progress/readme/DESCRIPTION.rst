This module adds a new `progress` field on `stock.picking`, `stock.move` and `stock.move.line`.

On `stock.move` and `stock.move.line`, this field represents the percentage of `qty_done` compared to
the `product_uom_qty`.
On `stock.picking`, this field is the average progress of all moves.
