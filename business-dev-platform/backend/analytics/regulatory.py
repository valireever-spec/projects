"""
German regulatory requirements by domain and legal form.
Data sourced from gesetze-im-internet.de and official German authorities.
"""


def german_requirements(domain: str, legal_form: str) -> dict:
    """
    Get German regulatory requirements for a domain and legal form.

    Args:
        domain: Business domain slug
        legal_form: One of (Einzelunternehmen, GbR, UG, GmbH, AG, Freiberufler)

    Returns:
        Dict with {
            requirements: [list of RegulatoryRequirement dicts],
            total_estimated_cost: EUR,
            total_estimated_days: days,
            grouped_by_category: {category: [requirements]}
        }
    """
    # Get base requirements by legal form
    legal_form_reqs = _get_legal_form_requirements(legal_form)

    # Get domain-specific requirements
    domain_reqs = _get_domain_specific_requirements(domain, legal_form)

    # Get tax requirements
    tax_reqs = _get_tax_requirements(legal_form)

    # Get DSGVO/data protection requirements
    dsgvo_reqs = _get_dsgvo_requirements()

    # Combine all
    all_reqs = legal_form_reqs + domain_reqs + tax_reqs + dsgvo_reqs

    # Calculate totals
    total_cost = sum(r.get("estimated_cost_eur", 0) for r in all_reqs)
    total_days = sum(r.get("estimated_days", 0) for r in all_reqs)

    # Group by category
    grouped = {}
    for req in all_reqs:
        category = req.get("category", "Sonstiges")
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(req)

    return {
        "domain": domain,
        "legal_form": legal_form,
        "requirements": all_reqs,
        "total_estimated_cost": total_cost,
        "total_estimated_days": total_days,
        "grouped_by_category": grouped,
        "completion_checklist": _build_checklist(all_reqs),
    }


def _get_legal_form_requirements(legal_form: str) -> list:
    """Get registration and setup requirements by legal form."""
    requirements_by_form = {
        "Einzelunternehmen": [
            {
                "category": "Registrierung",
                "requirement": "Gewerbeanmeldung beim Gewerbeamt",
                "authority": "Gewerbeamt vor Ort",
                "description": "Obligatorisch für jeden Gewerbetreibenden",
                "estimated_cost_eur": 50,
                "estimated_days": 3,
                "reference_url": "https://www.gesetze-im-internet.de/gewoin/",
            },
            {
                "category": "Registrierung",
                "requirement": "Anmeldung beim Finanzamt (Steuernummer)",
                "authority": "Finanzamt",
                "description": "Automatisch nach Gewerbeanmeldung, oder separat wenn freiberuflich",
                "estimated_cost_eur": 0,
                "estimated_days": 14,
                "reference_url": "https://www.gesetze-im-internet.de/estg/",
            },
        ],
        "Freiberufler": [
            {
                "category": "Registrierung",
                "requirement": "Anmeldung beim Finanzamt (Steuernummer)",
                "authority": "Finanzamt",
                "description": "Erforderlich für Freiberufler (Ärzte, Rechtsanwälte, Berater, Künstler, etc.)",
                "estimated_cost_eur": 0,
                "estimated_days": 14,
                "reference_url": "https://www.gesetze-im-internet.de/ustg_1980/",
            },
        ],
        "GbR": [
            {
                "category": "Registrierung",
                "requirement": "Eintrag ins Handelsregister (optional, aber empfohlen)",
                "authority": "Amtsgericht Handelsregister",
                "description": "Zivilgesellschaft, Handelsregistereintrag optional",
                "estimated_cost_eur": 300,
                "estimated_days": 10,
                "reference_url": "https://www.gesetze-im-internet.de/hgb/",
            },
            {
                "category": "Registrierung",
                "requirement": "Gewerbeanmeldung",
                "authority": "Gewerbeamt",
                "description": "Erforderlich bei Gewerbebetrieb",
                "estimated_cost_eur": 50,
                "estimated_days": 3,
                "reference_url": "https://www.gesetze-im-internet.de/gewoin/",
            },
        ],
        "UG": [
            {
                "category": "Registrierung",
                "requirement": "Notarielle Anmeldung und Handelsregistereintrag",
                "authority": "Amtsgericht + Notar",
                "description": "Mini-GmbH mit reduziertem Kapital (1 EUR möglich)",
                "estimated_cost_eur": 500,
                "estimated_days": 10,
                "reference_url": "https://www.gesetze-im-internet.de/gmbhg/",
            },
            {
                "category": "Registrierung",
                "requirement": "Anmeldung beim Finanzamt",
                "authority": "Finanzamt",
                "description": "Steuernummer und ggf. USt-Identifikationsnummer",
                "estimated_cost_eur": 0,
                "estimated_days": 14,
                "reference_url": "https://www.gesetze-im-internet.de/ustg_1980/",
            },
        ],
        "GmbH": [
            {
                "category": "Registrierung",
                "requirement": "Notarielle Gründung und Handelsregistereintrag",
                "authority": "Amtsgericht + Notar",
                "description": "Mindestkapital 25.000 EUR (oder 12.500 EUR bei UG)",
                "estimated_cost_eur": 800,
                "estimated_days": 14,
                "reference_url": "https://www.gesetze-im-internet.de/gmbhg/",
            },
            {
                "category": "Registrierung",
                "requirement": "Anmeldung beim Finanzamt",
                "authority": "Finanzamt",
                "description": "Körperschaftsteuer und Gewerbesteuer",
                "estimated_cost_eur": 0,
                "estimated_days": 14,
                "reference_url": "https://www.gesetze-im-internet.de/kstg_1960/",
            },
            {
                "category": "Registrierung",
                "requirement": "Gewerbeanmeldung",
                "authority": "Gewerbeamt",
                "description": "Erforderlich für Gewerbebetrieb",
                "estimated_cost_eur": 50,
                "estimated_days": 3,
                "reference_url": "https://www.gesetze-im-internet.de/gewoin/",
            },
        ],
        "AG": [
            {
                "category": "Registrierung",
                "requirement": "Notarielle Gründung und Handelsregistereintrag",
                "authority": "Amtsgericht + Notar",
                "description": "Mindestkapital 50.000 EUR",
                "estimated_cost_eur": 1500,
                "estimated_days": 21,
                "reference_url": "https://www.gesetze-im-internet.de/aktg/",
            },
            {
                "category": "Registrierung",
                "requirement": "Anmeldung beim Finanzamt",
                "authority": "Finanzamt",
                "description": "Körperschaftsteuer",
                "estimated_cost_eur": 0,
                "estimated_days": 14,
                "reference_url": "https://www.gesetze-im-internet.de/kstg_1960/",
            },
        ],
    }

    return requirements_by_form.get(legal_form, [])


def _get_domain_specific_requirements(domain: str, legal_form: str) -> list:
    """Get domain-specific licenses and requirements."""
    domain_reqs = {
        "consulting-gastronomie": [
            {
                "category": "Lizenzen & Genehmigungen",
                "requirement": "Gaststättenerlaubnis (§ 2 GastStättV)",
                "authority": "Ordnungsamt/Gewerbeamt",
                "description": "Erforderlich für Gaststättenbetrieb (wenn Getränkeverkauf)",
                "estimated_cost_eur": 200,
                "estimated_days": 30,
                "reference_url": "https://www.gesetze-im-internet.de/gastattenauv/",
            },
            {
                "category": "Lizenzen & Genehmigungen",
                "requirement": "Lebensmittelhygieneschulung",
                "authority": "Gesundheitsamt",
                "description": "Belehrung nach § 43 IfSG",
                "estimated_cost_eur": 100,
                "estimated_days": 5,
                "reference_url": "https://www.gesetze-im-internet.de/ifsg/",
            },
        ],
        "psychologische-beratung": [
            {
                "category": "Lizenzen & Genehmigungen",
                "requirement": "Heilpraktikererlaubnis (optional, aber hilfreich)",
                "authority": "Gesundheitsamt",
                "description": "Nicht immer erforderlich, aber empfohlen",
                "estimated_cost_eur": 300,
                "estimated_days": 60,
                "reference_url": "https://www.gesetze-im-internet.de/hpr/",
            },
        ],
        "immobilien-makler": [
            {
                "category": "Lizenzen & Genehmigungen",
                "requirement": "Maklererlaubnis nach § 34c GewO",
                "authority": "Industrie- und Handelskammer (IHK)",
                "description": "Erforderlich für Makler, Darlehensvermittler",
                "estimated_cost_eur": 500,
                "estimated_days": 30,
                "reference_url": "https://www.gesetze-im-internet.de/gewo/__34c.html",
            },
            {
                "category": "Versicherungen",
                "requirement": "Maklerversicherung und Kundengeldverwaltung",
                "authority": "Versicherungsunternehmen",
                "description": "Pflicht zur Absicherung von Kundengeldern",
                "estimated_cost_eur": 1000,
                "estimated_days": 14,
                "reference_url": "https://www.gesetze-im-internet.de/gewo/__34c.html",
            },
        ],
        "accounting-dienstleistung": [
            {
                "category": "Lizenzen & Genehmigungen",
                "requirement": "Steuerberatererlaubnis (§ 4 StBerG) oder Buchhalter-Zertifizierung",
                "authority": "Steuerberaterkammer",
                "description": "Für umfassende Steuerberatung erforderlich",
                "estimated_cost_eur": 5000,
                "estimated_days": 180,
                "reference_url": "https://www.gesetze-im-internet.de/stberg_2012/",
            },
        ],
    }

    return domain_reqs.get(domain, [])


def _get_tax_requirements(legal_form: str) -> list:
    """Get tax-related requirements by legal form."""
    tax_reqs = {
        "Einzelunternehmen": [
            {
                "category": "Steuern",
                "requirement": "Einkommensteuer (ESt) Erklärung",
                "authority": "Finanzamt",
                "description": "Jährliche Steuererklärung erforderlich",
                "estimated_cost_eur": 200,  # Professional help cost
                "estimated_days": 30,
                "reference_url": "https://www.gesetze-im-internet.de/estg/",
            },
            {
                "category": "Steuern",
                "requirement": "Umsatzsteuer (USt) Anmeldung",
                "authority": "Finanzamt",
                "description": "Monatlich oder vierteljährlich je nach Umsatz",
                "estimated_cost_eur": 50,
                "estimated_days": 0,
                "reference_url": "https://www.gesetze-im-internet.de/ustg_1980/",
            },
        ],
        "GmbH": [
            {
                "category": "Steuern",
                "requirement": "Körperschaftsteuer (KSt) Erklärung",
                "authority": "Finanzamt",
                "description": "Jährlich erforderlich (Mindestbesteuerung 15%)",
                "estimated_cost_eur": 500,
                "estimated_days": 30,
                "reference_url": "https://www.gesetze-im-internet.de/kstg_1960/",
            },
            {
                "category": "Steuern",
                "requirement": "Gewerbesteuer (GewSt) Erklärung",
                "authority": "Finanzamt",
                "description": "Je nach Gemeinde, durchschnittlich 14%",
                "estimated_cost_eur": 300,
                "estimated_days": 30,
                "reference_url": "https://www.gesetze-im-internet.de/gewerbesteuerg/",
            },
            {
                "category": "Steuern",
                "requirement": "Umsatzsteuer (USt) Anmeldung",
                "authority": "Finanzamt",
                "description": "Monatlich oder vierteljährlich",
                "estimated_cost_eur": 50,
                "estimated_days": 0,
                "reference_url": "https://www.gesetze-im-internet.de/ustg_1980/",
            },
        ],
        "AG": [
            {
                "category": "Steuern",
                "requirement": "Körperschaftsteuer (KSt) Erklärung",
                "authority": "Finanzamt",
                "description": "Jährlich erforderlich",
                "estimated_cost_eur": 800,
                "estimated_days": 30,
                "reference_url": "https://www.gesetze-im-internet.de/kstg_1960/",
            },
            {
                "category": "Steuern",
                "requirement": "Gewinnabführungsvertrag (optional)",
                "authority": "Finanzamt",
                "description": "Falls relevant für Konzernstruktur",
                "estimated_cost_eur": 500,
                "estimated_days": 14,
                "reference_url": "https://www.gesetze-im-internet.de/kstg_1960/",
            },
        ],
    }

    return tax_reqs.get(legal_form, [])


def _get_dsgvo_requirements() -> list:
    """Get DSGVO/data protection requirements (apply to all)."""
    return [
        {
            "category": "Datenschutz & Compliance",
            "requirement": "Datenschutzerklärung (DSGVO)",
            "authority": "Keine (Selbstverpflichtung)",
            "description": "Erforderlich für Website/Online-Präsenz",
            "estimated_cost_eur": 200,
            "estimated_days": 5,
            "reference_url": "https://www.gesetze-im-internet.de/dsgvo/",
        },
        {
            "category": "Datenschutz & Compliance",
            "requirement": "Impressum (TMG)",
            "authority": "Keine",
            "description": "Erforderlich für Website und E-Mails",
            "estimated_cost_eur": 0,
            "estimated_days": 1,
            "reference_url": "https://www.gesetze-im-internet.de/tmg/",
        },
        {
            "category": "Datenschutz & Compliance",
            "requirement": "AGB (Allgemeine Geschäftsbedingungen)",
            "authority": "Keine",
            "description": "Empfohlen für B2C/B2B Geschäfte",
            "estimated_cost_eur": 300,
            "estimated_days": 7,
            "reference_url": "https://www.gesetze-im-internet.de/bgb/",
        },
        {
            "category": "Datenschutz & Compliance",
            "requirement": "Datenschutzbeauftragte (optional, ab 20 Beschäftigte)",
            "authority": "Aufsichtsbehörden",
            "description": "Ab bestimmter Beschäftigtenzahl erforderlich",
            "estimated_cost_eur": 2000,
            "estimated_days": 0,
            "reference_url": "https://www.gesetze-im-internet.de/dsgvo/artikel_37.html",
        },
    ]


def _build_checklist(requirements: list) -> list:
    """Build a simple yes/no checklist."""
    return [
        {
            "item": req.get("requirement", ""),
            "category": req.get("category", ""),
            "completed": False,
            "due_date": None,
        }
        for req in requirements
    ]
