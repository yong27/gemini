##############################
Loading a VCF file into Gemini
##############################


==============================
The basics
==============================

Before we can use Gemini to explore genetic variation, we must first ``load`` our 
VCF file into the Gemini database framework.  We expect you to have first 
annotated the functional consequence of each variant in your VCF using either 
VEP or snpEff (Note that v3.0+ of snpEff is required to track the amino acid 
length of each impacted transcript). Logically,the loading step is done with 
the ``gemini load`` command.  Below are two examples based on a VCF file that 
we creatively name my.vcf.  The first example assumes that the VCF has been 
pre-annotated with VEP and the second assumes snpEff.

.. code-block:: bash

	# VEP-annotated VCF
	$ gemini load -v my.vcf -t VEP my.db

	# snpEff-annotated VCF
	$ gemini load -v my.vcf -t snpEff my.db

================================
Using multiple CPUS for loading
================================

Now, the loading step is very computationally intensive and thus can be very slow
with just a single core.  However, if you have more CPUs in your arsenal,
you specify more cores.  This provides a roughly linear increase in speed as a 
function of the number of cores. On our local machine, we are able to load a 
VCF file derived from the exomes of 60 samples in about 10 minutes.  With a 
single core, it takes a few hours.


.. note::

    Using multiple cores requires that you have both the ``bgzip`` tool from 
    `tabix <http://sourceforge.net/projects/samtools/files/tabix/>`_ and the 
    `grabix <https://github.com/arq5x/grabix>`_ tool installed in your PATH.

.. code-block:: bash

    $ gemini load -v my.vcf -t snpEff --cores 20 my.db

As each variant is loaded into the ``gemini`` database framework, it is being 
compared against several annotation files that come installed with the software.  
We have developed an annotation framework that leverages 
`tabix <http://sourceforge.net/projects/samtools/files/tabix/>`_, 
`bedtools <http://bedtools.googlecode.com>`_, and 
`pybedtools <http://pythonhosted.org/pybedtools/>`_ to make things easy and 
fairly performant. The idea is that, by augmenting VCF files with many
informative annotations, and converting the information into a ``sqlite`` 
database framework, ``gemini`` provides a flexible 
database-driven API for data exploration, visualization, population genomics 
and medical genomics.  We feel that this ability to integrate variation
with the growing wealth of genome annotations is the most compelling aspect of 
``gemini``.  Combining this with the ability to explore data with SQL 
using a database design that can scale to 1000s of individuals (genotypes too!)
makes for a nice, standardized data exploration system.


===================================
Describing samples with a PED file
===================================
To do.


===================================
Loading VCFs without genotypes.
===================================
To do.