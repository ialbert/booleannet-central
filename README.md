Boolean Network Modeling
========================

The goal of this software package is to provide intuitive and accessible tools for simulating *biological regulatory networks*
in a boolean formalism. Using this simulator biologist and bioinformaticians can specify their system in a simple textual language then
explore various dynamic behaviors via a web interface or an application programming interface (API) each designed to facilitate scientific discovery,
data collection and reporting.

The software is primarly distributed as [http://www.python.org Python] source code and requires that [http://www.python.org Python 3] (or later)
be installed on the target computer.

Latest release *1.2.7*, April 24th, 2014

Download the library:

Installation
------------

	pip install BooleanNet

Download distribution:

https://drive.google.com/folderview?id=0B1Q2dBPeRlunQndRVzVNZHlGQkk

Bugfix Note
-----------

January 7, 2010. Please note that versions 1.2.0 to 1.2.4 of the BooleanNet package have  a bug that cause the node updates to execute in original (listed) order during the first iteration, before randomizing the order of nodes for subsequent iterations. This bug affects only the asynchronous update mechanism. 

The net effect of the bug is that for certain type of rules the first execution of them may funnel the states into the basin of one of the attractors. Overall the answers will not be incorrect but, depending on the rules and order of nodes they may be incomplete. Please update to the latest version. My apologies. Istvan Albert

Publication
-----------

[Boolean network simulations for life scientist](http://www.scfbm.org/content/3/1/16) by István Albert, Juilee Thakar, Song Li, Ranran Zhang, and Réka Albert in *Source Code for Biology and Medicine (2008)* 

Introduction
------------

When trying to understand the role and functioning of a regulatory network,
the first step is to assemble the components of the network and the interactions
between them. The experimental advances in the large scale mapping of regulatory networks are fairly recent, but modeling efforts date back to the end of 1960s thanks to the pioneering work of Stuart Kauffman and Rene Thomas.

In a Boolean representation we assume that nodes are equivalent, and their interactions form a directed graph in which each node receives inputs from its neighbors (nodes that are connected to it). The state of nodes is described by binary (ON/OFF) variables, and the dynamic behavior of each variable, that is, whether it will be ON or OFF at next moment, is governed by a Boolean function. In general, a Boolean or logical function is written as a statement acting on the inputs using the logical operators *and*, *or* and *not* and its output is ON(OFF) if the statement is true (false).


Documentation
--------------

A [http://atlas.bx.psu.edu/booleannet/booleannet.html detailed documentation] is available on our external website. This documentation is also included in the source code distribution. See the:

  * [http://atlas.bx.psu.edu/booleannet/booleannet.html#Installation Installation] 
  * [http://atlas.bx.psu.edu/booleannet/booleannet.html#Tutorials Tutorials] 

for a quick overview on how the make the library work for you. 

About the library
-----------------

*Note* as of version 1.2 (Nov 12, 2008) the library has acquired several new features (see below) and underwent a substantial reorganization. To keep old code from interfering with new one the library namespace has been changed to *boolean2*

In this software package, we implement mutliple advanced methodologies which combine discrete logical rules with more realistic assumptions regarding the relative timescales of the  processes:

  * *synchronous* updates are performed in listed order, but the states change only at the end of the update round
  * *asynchronous* updates are performed in random order and the states immediately reflect the changes, this makes the model stochastic. 
  * *ranked asynchronous* updates are performed in rank order, within the same rank the updates take place asynchronously
  * *time synchronous* update are performed in time. Each rule has a time delay associated with them, updates take place at multiples of these delays
  * *piece wise differential* updates associate a set of continuous variables (concentrations, decay rates and thresholds) to each discrete variable in the system. The dynamics of these continuous variables is determined by a _linear system of piecewise differential equations_, leading to a *hybrid model* in the manner first suggested by Leon Glass and collaborators.

http://booleannet.googlecode.com/svn/webdata/example-hybrid-override.png

Example Rules
-------------

Here are a few example rules for *BooleanNet* covering various research projects. Most of these rules were collected via a thorough literature search and were manually curated into their final form. These rules are available in the *examples/samples* directory of the source code distribution.


 * Rules for abscicis acid induced stomatal closure in plants  *[http://booleannet.googlecode.com/svn/webdata/aba.txt aba.txt]* published as _Song Li, Sarah Assmann and Réka Albert *Predicting essential components of signal transduction networks: dynamic model of guard cell abscisic acid signaling* PLoS Biology 4 (10): e312, 2006_
 
 * Rules for T-cell large granular lymphocyte leukemia simulation  *[http://booleannet.googlecode.com/svn/webdata/LGL.txt LGL.txt]* published as _Ranran Zhang, Mithun Vinod Shah, Jun Yang, Susan B. Nyland, Xin Liu, Jong K. Yun, Réka Albert, and Thomas P. Loughran, Jr. *Network Model of Survival Signaling in LGL Leukemia* PNAS, 2008 (to appear)_

 * Rules for mammalian immune response to B. bronchiseptica infection  *[http://booleannet.googlecode.com/svn/webdata/immune.txt immune.txt]* published as _J. Thakar, M. Pilione, G. Kirimanjeswara, E. Harvill and R. Albert *Modeling Systems-Level Regulation of Host Immune Responses* PLoS Computational Biology 6, e109 (2007_
 
Some of the resulting plots based on the rules above:

http://booleannet.googlecode.com/svn/webdata/footer.png 

Credits
-------

The library has been designed and implemented by *[http://www.personal.psu.edu/iua1/ István Albert]* using previous work, ideas and contributions from:
  * *Song Li*
  * *[http://www.phys.psu.edu/%7Ejthakar/ Juilee Thakar]*
  * *Ranran Zhang*
  * *Assieh Saadatpour Moghaddam* 

None of us would be thinking about Boolean Networks if it weren't for *[http://www.phys.psu.edu/~ralbert/ Réka Albert]*.

Our software relies on the following third party libraries that are distributed with  the software:

  * [http://www.dabeaz.com/ply/ PLY] by *David Beazley*

The following library must be also installed if the engine will be used in `plde` mode (piece-wise linear differential equations):

  * [http://matplotlib.sourceforge.net/ matplotlib] by Dave Hunter
