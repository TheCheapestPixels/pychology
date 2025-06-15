Utility AI
----------

While Behavior Trees are a powerful way to structure an AI's reasoning,
they are basically a thin syntactic layer that adapts the concepts of
flow control to an environment in which time exists. Implementing a
Behavior Tree is conceptually not too different from hardcoding an AI's
behavior in code; There is precious little abstraction going on.

Utility AI is a way to make the decision on which action to pursue based
on the more abstract concept of considerations. The basic approach is
this:
* A `Reasoner` is an AI that has a set of `Options`, which are the
  available actions.
* Each `Option` is assigned a set of `Considerations`, which calculates
  a utility value based on the current circumstances. Typically, these
  values are floating point numbers in the `[0.0, 1.0]` range.
* To prepare for choosing an `Option`, for each `Option`, the utility of
  each of its `Considerations` is calculated, and the results are
  multiplied, yielding the utility of the `Option` as a whole.
* There are two basic ways to make the final choice:
  * Absolute value: Just choose the highest-scored `Option`.
  * Relative value: A weighted random choice is made between the
    `Options`, with the weight of each being its utility value.

Both of these approaches to choosing an `Option` have drawbacks. When
using only the absolute value, the AI will behave optimally and
predictably, but this can also be rather boring in the context of games.
When using only the relative value, low-valued `Options` may be selected
because the choice is in the end random, resulting in an AI that acts
chaotically and disorganized.

A typical approach to tune the behavior within this spectrum is to take
only a subset of `Options` into consideration for the choice, e.g. "the
three highest-valued ones" ot "those with a value of at least 80% of the
highest-valued one", and make a weighted random choice between these.

`pychology` uses the Dual Utility Reasoner. Its `Options` use two values
to express their utility, namely rank and weight. Rank is used for the
preselection, in that only the `Options` with the highest rank will be
considered for selection; Weight operates just like utility for the
purpose of then making the final choice. `Considerations` in turn return
three values, namely
* rank, where an `Option's` rank is the highest of the ranks of its
  `Considerations`,
* bonus, which is typically 0.0 for each consideration except the tuning
  consideration, where it is 1.0; The boni of all considerations get
  summed up, typically resulting in 1.0. This then acts as a factor to
  the `Option's` weight. While best ignored most of the time, the bonus
  can be used as a way to give an option a lot more weight under some
  circumstance.
* multiplier, which is basically the utility as laid out above, and gets
  multiplied with the bonus.

Looked at again from the bottom up, ...
* `Considerations` return rank, bonus, and multiplier, which an...
* `Option` combines into rank and weight by using the highest rank
  value, and the sum of the boni times all multipliers.
* The `Reasoner` then takes the `Options` with the highest rank and
  makes a weighted random choice between them; In the case that all
  options with the highest rank have a weight of `0.0`, it will consider
  the next-highest, and so on.
  FIXME: If all ranks are empty, should that throw an `Exception` or
  return a default plan? Right now, it causes a `ValueError` in the
  decider.

With this approach, a designer can sort `Options` into ranks by their
urgency (which may vary based on circumstances), and then design their
utility as usual, resulting in a behavior that is both superficially
believable and apparently spontaneous.

Additionally, the Dual Utility Reasoner allows to address several
recurring problems in behavior design by using a set of design patterns
for utility functions.
