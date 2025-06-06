from smolagents import tool
from owlready2 import get_ontology


def load_edam_ontology():
    """
    Loads the EDAM ontology OWL file from GitHub using owlready2.
    
    Returns:
        Ontology: The loaded EDAM ontology object, or None if loading fails
    """
    # URL to the raw EDAM ontology OWL file
    url = "https://raw.githubusercontent.com/edamontology/edamontology/main/releases/EDAM_1.25.owl"
    
    try:
        # Load the ontology directly from the URL
        onto = get_ontology(url).load()
        print(f"Successfully loaded EDAM ontology: {onto}")
        return onto
    except Exception as e:
        print(f"Error loading EDAM ontology: {e}")
        return None

@tool
def search_edam_ontology_by_search_term(search_term: str = None) -> list:
    """
    Generic function to search by EDAM entity type using native search. The native search is strict so you need to provide single word search terms (for example: 'fasta').
    
    Args:
        search_term: single word search term to filter results
    
    Returns:
        list: List of matching classes
    """
    onto = load_edam_ontology()
    entity_type = "format"
    # Search using IRI pattern matching
    pattern = f"*{entity_type}_*"
    matches = onto.search(iri=pattern)
    
    # Filter by search term if provided
    if search_term:
        search_term_lower = search_term.lower()
        filtered_matches = []
        
        for match in matches:
            # Check name
            if search_term_lower in match.name.lower():
                filtered_matches.append(match)
                continue
                
            # Check labels
            if hasattr(match, 'label') and match.label:
                for label in match.label:
                    if search_term_lower in str(label).lower():
                        filtered_matches.append(match)
                        break
        
        matches = filtered_matches
    
    # Print results  
    search_desc = f" matching '{search_term}'" if search_term else ""
    print(f"\nFound {len(matches)} {entity_type}(s){search_desc}:")
    for i, match in enumerate(matches[:10]):  # Limit to 10 for readability
        print(f"{i+1}. {match.name}")
        if hasattr(match, 'label') and match.label:
            print(f"   Label: {match.label[0]}")
        print()
    
    if len(matches) > 10:
        print(f"... and {len(matches) - 10} more results")
    
    return matches

@tool
def get_edam_description_from_ontology_format_class(term_id: str) -> str:
    """
    Simple function to get the description (label) of an EDAM ontology term, input should be the ontology class name (for example: 'format_1930'), use this tool to double check if an ontology is correct.
    
    Args:
        term_id: EDAM term ID like "format_1930" or "data_1234"
    
    Returns:
        str: The description/label of the term, or None if not found
    """
    onto = load_edam_ontology()
    if not onto:
        return None
    
    try:
        # Get the class directly by name
        term_class = getattr(onto, term_id)
        
        # Try to get hasDefinition first (detailed description)
        if hasattr(term_class, 'hasDefinition') and term_class.hasDefinition:
            return str(term_class.hasDefinition[0])
        
        # Fall back to comment if no definition
        elif hasattr(term_class, 'comment') and term_class.comment:
            return str(term_class.comment[0])
        
        # Fall back to label if no comment or definition
        elif hasattr(term_class, 'label') and term_class.label:
            return str(term_class.label[0])
        
        else:
            return f"No description found for {term_id}"
            
    except AttributeError:
        return f"Term {term_id} not found in EDAM ontology"
