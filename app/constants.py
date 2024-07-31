# app/constants.py

WEB_TYPES = ['rest', 'web', 'app', 'suite', 'workbench', 'db', 'soap', 'sparql']

STRUCT_META = ['biotools', 'bioconda', 'github', 'bitbucket', 'galaxy', 'toolshed', 'opeb_metrics', 'observatory']


# For determining if a software is discoverable/searchable in common software registries, we use a list of the most commonly used and popular registries and package managers. 
# These would include well-known programming language package managers, bioinformatics repositories, and container registries.
SOFT_REG =  [
    'NPM',               # Node.js packages
    'PyPI',              # Python packages
    'RubyGems',          # Ruby packages
    'Packagist',         # PHP packages
    'Maven',             # Java packages
    'NuGet',             # .NET packages
    'CRAN',              # R packages
    'CocoaPods',         # CocoaPods for Objective-C and Swift
    'DockerHub',         # Container images
    'BioTools',          # Bioinformatics tools
    'Bioconda',          # Bioinformatics packages
    'Bioconductor',      # Bioinformatics software
    'GitHub',            # GitHub repositories
    'GitLab',            # GitLab repositories
    'Bitbucket',         # Bitbucket repositories
    'SourceForge',       # Open source projects
    'Crates',            # Rust packages
    'Conda',             # Package management system
    'Spack',             # HPC package management
    'Chocolatey',        # Windows package manager
    'Homebrew',          # macOS package manager
    'Snap',              # Snappy package management system
    'Flatpak',           # Flatpak application distribution
    'JFrog',             # JFrog Artifactory
    'Nexus',             # Sonatype Nexus Repository
    'Toolshed',          # Galaxy Tool Shed
    'BioContainers',     # BioContainers
    'GitHub Container Registry', # GitHub Container Registry
    'GitLab Container Registry', # GitLab Container Registry
]

DEPENDENCIES_AWARE_SYSTEMS = [
    'Toolshed', 
    'Bioconductor', 
    'Conda', 
    'PyPI', 
    'CRAN', 
    'NPM', 
    'CPAN', 
    'RubyGems', 
    'DockerHub', 
    'GitHub Container Registry', 
    'GitLab Container Registry', 
    'BioContainers',
    'Maven',              # Java
    'NuGet',              # .NET
    'Packagist',          # PHP
    'Hex',                # Elixir
    'Cargo',              # Rust
    'Hackage',            # Haskell
    'CRAN',               # R
    'SBT',                # Scala
    'Bower',              # Web front-end
    'JSPM',               # JavaScript
    'Spack',              # Scientific software
    'Homebrew',           # macOS
    'Debian',             # Debian packages
    'RPM',                # Red Hat packages
    'APK',                # Alpine Linux packages
    'Bazel',              # Build system
    'Swift Package Manager', # Swift
    'Vcpkg',              # C++
    'Nimble',             # Nim
    'Dub'                 # D
]

DOWNLOADABLE_SOURCES = ['bioconda', 'bioconductor', 'galaxy', 'toolshed', 'bioconda_conda', 'bioconda_recipes']


FREE_OS = free_operating_systems = [
    "Linux",
    "FreeBSD",
    "OpenBSD",
    "NetBSD",
    "DragonFly BSD",
    "ReactOS",
    "Haiku"
]
E_INFRASTRUCTURES = [
    'vre.multiscalegenomics.eu', 
    'galaxy.', 
    'usegalaxy.'
    ]

NO_GUIDE = [
    'License', 
    'Terms of Use', 
    'News', 
    'Contribution', 
    'Citation', 
    'Contact', 
    'Changelog', 
    'Release', 
    'FAQ', 
    'Support', 
    'Installation', 
    'Troubleshooting', 
    'Privacy Policy', 
    'Disclaimer', 
    'API Reference', 
    'Getting Started', 
    'Tutorial', 
    'Overview', 
    'Specification', 
    'Developer Guide', 
    'Maintainer Guide'
]

PERMISSIONS_TYPES = [
    # License variations and synonyms
    'License',
    'Licensing Agreement',
    'Software License',
    'Usage License',
    'End User License Agreement',
    'User License',
    'Licensing Terms',
    'Permission',
    'Authorization',
    'Right to Use',
    'Usage Rights',
    'Access License',
    'Distribution License',
    'Grant of License',
    'License Agreement',
    'License Terms',
    
    # Terms of Use variations and synonyms
    'Terms of Use',
    'Terms and Conditions',
    'User Agreement',
    'Usage Terms',
    'Service Terms',
    'User Terms',
    'Terms of Service',
    'Usage Agreement',
    'Terms',
    'Service Agreement',
    'Conditions of Use',
    'End User Agreement',
    'Terms and Policies',
    'User Policies',
    'Access Terms',
    'Platform Terms',
    
    # Conditions of Use variations and synonyms
    'Conditions of Use',
    'Usage Conditions',
    'Terms and Conditions',
    'User Conditions',
    'Service Conditions',
    'Use Conditions',
    'Conditions',
    'User Terms',
    'Service Terms',
    'Usage Terms',
    'Access Conditions',
    'User Guidelines',
    'Terms of Service',
    'End User Conditions',
    'Terms and Policies',
    'User Agreement'
]

VERIFIABLE_FORMATS = [
    'json',     # JavaScript Object Notation
    'xml',      # Extensible Markup Language
    'rdf',      # Resource Description Framework
    'xds',      # XML Data Structure
    'yaml',     # YAML Ain't Markup Language
    'avro',     # Apache Avro
    'protobuf', # Protocol Buffers
    'parquet',  # Apache Parquet
    'hdf5',     # Hierarchical Data Format version 5
    'toml',     # Tom's Obvious, Minimal Language
    'bson',     # Binary JSON
    'msgpack',  # MessagePack
    'cbor',     # Concise Binary Object Representation
    'excel',    # Microsoft Excel formats (xls, xlsx)
    'netcdf',   # Network Common Data Form
    'mat',      # MATLAB format
    'sql',      # Structured Query Language format dumps
    'orc'       # Optimized Row Columnar format
]



SOURCES_LABELS = {
    'BIOCONDUCTOR': 'bioconductor',
    'BIOCONDA': 'bioconda',
    'BIOTOOLS': 'biotools',
    'TOOLSHED': 'toolshed',
    'GALAXY_METADATA': 'galaxy_metadata',
    'SOURCEFORGE': 'sourceforge',
    'GALAXY_EU': 'galaxy',
    'OPEB_METRICS': 'opeb_metrics',
    'BIOCONDA_RECIPES': 'bioconda_recipes',
    'BIOCONDA_CONDA': 'bioconda_conda',
    'REPOSITORIES': 'repository',
    'GITHUB': 'github',
    'BITBUCKET': 'bitbucket'
}

SOURCES_TO_TRANSFORM = [
    'BIOCONDUCTOR', 'BIOCONDA', 'BIOTOOLS', 'TOOLSHED', 'GALAXY_METADATA', 'SOURCEFORGE',
    'GALAXY_EU', 'OPEB_METRICS', 'BIOCONDA_RECIPES', 'BIOCONDA_CONDA', 'REPOSITORIES',
    'GITHUB', 'BITBUCKET'
]
