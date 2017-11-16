#! /usr/bin/env python

import datajoint as dj

schema = dj.schema('catalog_ret1', locals())


@schema
class Lab(dj.Manual):
    definition = """
    # Lab
    lab                 : varchar(255)            # lab conducting the study
    ----
    institution         : varchar(255)            # sponsoring institution
    """


@schema
class Keyword(dj.Lookup):
    definition = """
    # Study Keywords
    keyword             : varchar(24)             # study types
    """
    contents = zip(['behavior', 'extracellular', 'photostim'])


@schema
class Study(dj.Manual):
    definition = """
    # Study
    study               : varchar(8)              # short name of the study
    ---
    study_description   : varchar(255)            # detailed study description
    -> Lab
    reference_atlas     : varchar(255)            # e.g. "paxinos"
    """


@schema
class StudyKeyword(dj.Manual):
    definition = """
    # Study keyword (see general/notes)
    -> Study
    -> Keyword
    """
    # XXX: empty


@schema
class Publication(dj.Manual):
    definition = """
    # Publication
    doi                 : varchar(60)             # publication DOI
    ----
    full_citation       : varchar(4000)
    authors=''          : varchar(4000)
    title=''            : varchar(1024)
    """
    # XXX: empty


@schema
class RelatedPublication(dj.Manual):
    definition = """
    -> Study
    -> Publication
    """
    # XXX: empty


@schema
class AnimalSource(dj.Lookup):
    definition = """
    animal_source       : varchar(30)
    """
    contents = zip(['unknown', 'JAX'])


@schema
class Strain(dj.Lookup):
    definition = """
    # Mouse strain
    strain              : varchar(30)             # mouse strain
    """
    contents = zip(['kj18', 'kl100', 'ai32', 'pl56'])


@schema
class GeneModification(dj.Lookup):
    definition = """
    gene_modification   : varchar(60)
    """
    contents = zip(['sim1-cre', 'rbp4-cre', 'chr2-eyfp', 'tlx-cre'])


@schema
class User(dj.Lookup):
    definition = """
    # User (lab member)
    username            : varchar(16)             #  database username
    ----
    full_name=''        : varchar(60)
    """


@schema
class Subject(dj.Manual):
    definition = """
    subject_id          : int                     # institution animal ID
    ---
    species             : varchar(30)
    date_of_birth       : date
    sex                 : enum('M','F','Unknown')
    ->                  [nullable]              AnimalSource
    """

    class GeneModification(dj.Part):
        definition = """
        # Subject gene modifications
        -> Subject
        -> GeneModification
        """
        # XXX: empty

    class Strain(dj.Part):
        definition = """
        -> Subject
        -> Strain
        """
        # XXX: empty


@schema
class Session(dj.Manual):
    definition = """
    -> Subject
    session:            int
    ---
    -> Study
    record:             int
    sample:             int
    session_date:       date		# session date
    session_suffix:     char(2)         # suffix for disambiguating sessions
    (experimenter)      -> User
    session_start_time: datetime
    """


@schema
class Ephys(dj.Manual):

    definition = """
    -> Session
    """

    class Electrode(dj.Part):
        definition = """
        -> Ephys
        electrode       : tinyint       # electrode no
        ---
        electrode_x     : decimal(5,2)  # (x in mm)
        electrode_y     : decimal(5,2)	# (y in mm)
        """

    # XXX: do we actually have a cell mapping in dataset?
    class Mapping(dj.Part):
        definition = """
        -> Ephys
        """

    class Unit(dj.Part):
        definition = """
        -> Ephys
        cell_no         : int		# cell no
        """

    class Spikes(dj.Part):
        definition = """
        -> Ephys.Unit
        ---
        spike_times     : longblob	# all events
        """


@schema
class Movie(dj.Manual):
    definition = """
    movie_id		: smallint	# movie IDs
    ----
    x			: int
    y			: int
    dx			: int
    dy			: int
    dim_a		: int
    dim_b		: int
    bpp			: tinyint	# bits per pixel
    pixel_size		: decimal(3,2)	# (mm)
    movie		: longblob	# 3d array
    source_fname	: varchar(255)	# source file
    """


@schema
class Stimulus(dj.Manual):

    definition = """
    -> Session
    """

    class Trial(dj.Part):

        # XXX: len(timestamps) varies w/r/t len(movie); timestamps definitive
        # ... actually 'num_samples' definitive, but same as len(timestamps)
        #     and so is redundant and discarded.

        definition = """
        -> Stimulus
        trial_idx	: smallint	# trial within a session
        ---
        -> Movie
        start_time	: float		# (s)
        stop_time	: float		# (s)
        timestamps	: longblob	# (s)
        """


@schema
class RF(dj.Computed):
    definition = """
    # Receptive Fields
    -> Ephys
    -> Stimulus
    """

    class Unit(dj.Part):
        definition = """
        # Receptive fields
        -> RF
        -> Ephys.Spikes
        ----
        rf              : longblob      # computed RF
        """
