![Logo: A brain in a jar together with a blackboard with scribbles on it; The jar is connected by wires to an eye and a robotic arm.](./logo.png)

pychology
=========

Simple Python implementations of popular game AI techniques.


### Overview

There are several paradigms for modeling AIs that have become popular in
game development. Some of these are complementary, as they work on
different problem domains, while some model the same domain in different
ways. `pychology` aims to make AI development modular and reusable, so
that for each problem you can choose freely among the sensible options
while retaining already developed functionality.

The paradigms (intended to be) implemented in `pychology` are:
* Blackboards: Storage and coordination
* [Hierarchical Finite State Machines (HFSM)](./docs/hfsm.md): Switching
  between states based on current conditions.
* [Behavior Trees (BT)](./docs/behavior_trees.md): Decision trees with
  sequences, prioritization, failure, and waiting for things to finish.
* [Utility AI](./docs/utility.md): Choosing the best action for the
  current circumstances.
* [Search](./docs/search.md): Searching and valuing paths through
  graphs.
* Goal-Oriented Action Planning (GOAP): Leveraging Search to find a
  sequence of actions that make a goal be fulfilled.
* Hierarchical Task Network (HTN): GOAP on BTs.
* Hierarchical Goal Network (HGN): A goal can be decomposed into
  smaller, more specific goals.
* Goal-Driven Autonomy (GDA): HGN with monitoring the execution of the
  current plan, and re-strategizing if a failure occurs.
* Introspective Multistrategy Learning (IML): GDA where a failure is
  analyzed, and hypothetical explanations are generated.

As a keystone to these building blocks, `pychology` offers `BrainJar`, a
class that uses a blackboard as the AIs memory, its connection to the
wider game environment, and storage for the individual parts of its
thought process. The `BrainJar` also provides a top-level entry point to
trigger the AI's thought process.


### Current State

| Module                               | Implementation | De-/Serialization | Debugging | Documentation | GUI Integration |
| ------------------------------------ | -------------- | ----------------- | --------- | ------------- | --------------- |
| Blackboards                          | Alpha          | ---               | ---       | ---           | ---             |
| Hierarchical Finite State Machine    | Pre-alpha      | ---               | ---       | Overview      | ---             |
| Behavior Trees                       | RC             | Pre-alpha         | ---       | Overview      | ---             |
| Utility AI                           | Beta           | ---               | ---       | Overview      | ---             |
| Search                               | Alpha          | ---               | ---       | Chaos         | ---             |
| Goal-Oriented Action Planning        | ---            | ---               | ---       | ---           | ---             |
| Hierarchical Task Network            | ---            | ---               | ---       | ---           | ---             |
| Hierarchical Goal Network            | ---            | ---               | ---       | ---           | ---             |
| Goal-Driven Autonomy                 | ---            | ---               | ---       | ---           | ---             |
| Introspective Multistrategy Learning | ---            | ---               | ---       | ---           | ---             |
| BrainJar                             | Beta           | ---               | ---       | ---           | ---             |


TODO
----

* Project
  * Packaging
* Behavior Trees
  * Node types
    * Weighted Random Choice Multinode
    * Plugin point for adding subtrees at runtime; Might be sensible to
      have as a universal property?
* Blackboards
  * Path-like keys: Currently BB keys are like dict keys. They should be
    paths, so that e.g. a whole subtree can be pruned.
  * Hierarchical BBs; Inheriting fields from other BBs.
  * Services: Functions in fields that are evaluated the first time that
    they are checked, and reset at the beginning of an AI tick.
* Search
  * Algorithms
    * Alpha-Beta Pruning
    * Quiescence Search
    * Bidirectional Search
    * Pondering
      * State graph garbage collection
      * Reevaluation on change of player
    * Demonstrate machine learning wherever applicable
    * Counterfactual Regret Minimization
      * https://en.wikipedia.org/wiki/Regret_(decision_theory)
      * http://modelai.gettysburg.edu/2013/cfr/cfr.pdf
      * https://poker.cs.ualberta.ca/publications/NIPS07-cfr.pdf
      * https://towardsdatascience.com/counterfactual-regret-minimization-ff4204bf4205?gi=a09c56e9300c
    * Action selection: Shortest beat path
  * Search capabilities
    * State selection
      * Add priority queue
    * State evaluation
      * Rip win-based and MCTS evaluations out of games
    * Action evaluation
      * https://www.researchgate.net/profile/Paul-Purdom/publication/220091335_Experiments_on_Alternatives_to_Minimax/links/0912f51470146478b1000000/Experiments-on-Alternatives-to-Minimax.pdf
    * Analysis
      * Add timing again
      * Provide API to query for collected data
      * Make printing optional
  * Tooling
    * REPL
      * Command line arguments
	* Make more things available through `repl.assemble_search`.
      * Tournaments
        * Have visualizations for other games than "two players, draws
	  possible".
	* Reorder matches to build up results equally over all of them,
	  making results human-accessible earlier.
        * CSV / JSON output
  * Documentation
    * Separate course-style page
    * Docstrings; Especially descriptions of lists / dicts transferred.
  * Hacks
    * Early termination of expansion if the root node has only one
      action available.
    * A state, once expanded, is not used anymore, and can be removed
      from memory; Only its metadata is what we are after.
  * Compilation: Refactor code for use with Cython / PyPy / mypyc and
    test speed improvements
* [Whatever this is](https://www.youtube.com/watch?v=Z-xU96pAuqs)
* Tolman-Eichenbaum machine
  * https://web.archive.org/web/20200325015457id_/https://www.biorxiv.org/content/biorxiv/early/2019/09/16/770495.full.pdf
  * https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7707106/
