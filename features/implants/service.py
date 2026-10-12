from __future__ import annotations

from random import randint, sample

from core.database import SessionLocal
from core.enums import Category, Severity
from features.implants.models import ImplantModel, SideEffectModel
from features.implants.schemas import Implant, Prerequisites

IMPLANT_COUNT = 50

SIDE_EFFECT_TEMPLATES = (
    {
        "reference": "SE-MILD-HEADACHE",
        "name": "Headache",
        "severity": Severity.MILD,
        "description": "Light cranial pressure during initial calibration.",
    },
    {
        "reference": "SE-MODERATE-HEADACHE",
        "name": "Headache",
        "severity": Severity.MODERATE,
        "description": "Persistent pain after prolonged synchronization.",
    },
    {
        "reference": "SE-SEVERE-HEADACHE",
        "name": "Headache",
        "severity": Severity.SEVERE,
        "description": "Intense migraine triggered by neural overload.",
    },
    {
        "reference": "SE-MILD-NAUSEA",
        "name": "Nausea",
        "severity": Severity.MILD,
        "description": "Brief stomach discomfort after activation.",
    },
    {
        "reference": "SE-MODERATE-NAUSEA",
        "name": "Nausea",
        "severity": Severity.MODERATE,
        "description": "Noticeable nausea during sensor alignment.",
    },
    {
        "reference": "SE-SEVERE-NAUSEA",
        "name": "Nausea",
        "severity": Severity.SEVERE,
        "description": "Severe vestibular disruption requiring rest.",
    },
    {
        "reference": "SE-MILD-INFLAMMATION",
        "name": "Inflammation",
        "severity": Severity.MILD,
        "description": "Localized tissue warmth around the implant site.",
    },
    {
        "reference": "SE-MODERATE-INFLAMMATION",
        "name": "Inflammation",
        "severity": Severity.MODERATE,
        "description": "Persistent swelling around the interface.",
    },
    {
        "reference": "SE-SEVERE-INFLAMMATION",
        "name": "Inflammation",
        "severity": Severity.SEVERE,
        "description": "Acute inflammatory reaction requiring follow-up.",
    },
    {
        "reference": "SE-MILD-FATIGUE",
        "name": "Fatigue",
        "severity": Severity.MILD,
        "description": "Temporary drop in energy after implant activation.",
    },
    {
        "reference": "SE-MODERATE-FATIGUE",
        "name": "Fatigue",
        "severity": Severity.MODERATE,
        "description": "Persistent exhaustion after prolonged use.",
    },
    {
        "reference": "SE-SEVERE-FATIGUE",
        "name": "Fatigue",
        "severity": Severity.SEVERE,
        "description": "Severe depletion of energy requiring rest.",
    },
    {
        "reference": "SE-MILD-DIZZINESS",
        "name": "Dizziness",
        "severity": Severity.MILD,
        "description": "Brief disorientation during synchronization.",
    },
    {
        "reference": "SE-MODERATE-DIZZINESS",
        "name": "Dizziness",
        "severity": Severity.MODERATE,
        "description": "Short-lived balance disruption during synchronization.",
    },
    {
        "reference": "SE-SEVERE-DIZZINESS",
        "name": "Dizziness",
        "severity": Severity.SEVERE,
        "description": "Intense vertigo after calibration.",
    },
    {
        "reference": "SE-MILD-TREMORS",
        "name": "Tremors",
        "severity": Severity.MILD,
        "description": "Light involuntary movements after activation.",
    },
    {
        "reference": "SE-MODERATE-TREMORS",
        "name": "Tremors",
        "severity": Severity.MODERATE,
        "description": "Noticeable shaking during neural overload.",
    },
    {
        "reference": "SE-SEVERE-TREMORS",
        "name": "Tremors",
        "severity": Severity.SEVERE,
        "description": "Uncontrolled micro-movements following neural overload.",
    },
    {
        "reference": "SE-MILD-IRRITATION",
        "name": "Irritation",
        "severity": Severity.MILD,
        "description": "Localized discomfort around the implant interface.",
    },
    {
        "reference": "SE-MODERATE-IRRITATION",
        "name": "Irritation",
        "severity": Severity.MODERATE,
        "description": "Persistent irritation around the implant interface.",
    },
    {
        "reference": "SE-SEVERE-IRRITATION",
        "name": "Irritation",
        "severity": Severity.SEVERE,
        "description": "Intense local reaction requiring monitoring.",
    },
    {
        "reference": "SE-MILD-CONFUSION",
        "name": "Confusion",
        "severity": Severity.MILD,
        "description": "Temporary mental fog after recalibration.",
    },
    {
        "reference": "SE-MODERATE-CONFUSION",
        "name": "Confusion",
        "severity": Severity.MODERATE,
        "description": "Temporary cognitive fog during recalibration.",
    },
    {
        "reference": "SE-SEVERE-CONFUSION",
        "name": "Confusion",
        "severity": Severity.SEVERE,
        "description": "Severe disorientation requiring observation.",
    },
)

IMPLANT_NAMES = {
    Category.NEURAL: [
        "CortexLink",
        "Synapse Relay",
        "Myelin Mesh",
        "NeuroFuse",
        "Cranial Array",
        "Signal Lattice",
        "Axon Gate",
        "Cerebral Node",
        "Pulse Thread",
        "Thought Bridge",
    ],
    Category.SENSORY: [
        "Optic Bloom",
        "Auditory Lattice",
        "Tactile Veil",
        "Spectral Lens",
        "Sensory Mesh",
        "Retina Thread",
        "Vibrance Array",
        "Echo Crown",
        "Signal Bloom",
        "Perception Grid",
    ],
    Category.MOTOR: [
        "Torque Anchor",
        "Kinetic Spine",
        "Flexion Core",
        "Motion Tether",
        "Stride Relay",
        "Servo Thread",
        "Joint Matrix",
        "Power Lattice",
        "Muscle Sync",
        "Limb Mesh",
    ],
    Category.METABOLIC: [
        "Nutrient Gate",
        "Cellular Regulator",
        "Flux Array",
        "Metabolic Core",
        "Balance Mesh",
        "Biofilter Node",
        "Vital Lattice",
        "Assimilation Drive",
        "Homeostasis Thread",
        "Metabolic Crown",
    ],
    Category.CARDIOVASCULAR: [
        "Heartline Coil",
        "Pulse Beacon",
        "Vascular Mesh",
        "Flow Anchor",
        "Circulation Core",
        "Hemodynamic Thread",
        "Aortic Relay",
        "Cardio Lattice",
        "Pulse Matrix",
        "Valve Sync",
    ],
    Category.DERMAL: [
        "Skin Shield",
        "Thermal Veil",
        "Barrier Mesh",
        "Dermal Weave",
        "Shield Lattice",
        "Protective Thread",
        "Cell Guard",
        "Barrier Core",
        "Skin Relay",
        "Thermal Anchor",
    ],
}


def build_prerequisites(index: int) -> dict[str, int | None]:
    return {
        "minAge": 18 + (index % 5),
        "maxAge": 55 + (index % 15),
        "minSize": 145 + (index % 10),
        "maxSize": 190 + (index % 12),
        "minWeight": 45 + (index % 8),
        "maxWeight": 95 + (index % 10),
    }


def build_description(category: Category, name: str) -> str:
    benefit_map = {
        Category.NEURAL: "restores cortical signal fidelity and cuts synaptic delay during high-load neural tasks.",
        Category.SENSORY: "sharpens sensory input, stabilizes perception, and improves contextual awareness in noisy environments.",
        Category.MOTOR: "increases biomechanical control, smooths movement, and reduces fatigue under sustained exertion.",
        Category.METABOLIC: "regulates nutrient transfer and keeps homeostatic rhythms stable during stress or recovery.",
        Category.CARDIOVASCULAR: "supports circulatory efficiency and maintains reliable flow under prolonged physical demand.",
        Category.DERMAL: "improves barrier resilience and thermal control while reducing irritation and tissue stress.",
    }

    category_label = {
        Category.NEURAL: "neural implant",
        Category.SENSORY: "sensory implant",
        Category.MOTOR: "motor implant",
        Category.METABOLIC: "metabolic implant",
        Category.CARDIOVASCULAR: "cardiovascular implant",
        Category.DERMAL: "dermal implant",
    }

    return (
        f"{name} is a {category_label[category]} designed for users who need reliable performance "
        f"in demanding conditions. It {benefit_map[category]}"
    )


def build_implant(index: int) -> ImplantModel:
    categories = list(Category)
    category = categories[index % len(categories)]
    name = IMPLANT_NAMES[category][index % len(IMPLANT_NAMES[category])]

    implant = ImplantModel(
        reference=f"REF{index + 1:03d}",
        name=name,
        description=build_description(category, name),
        category=category,
        prerequisites=build_prerequisites(index),
    )

    # implant.side_effects = [
    #     SideEffectModel(
    #         reference=f"{template['reference']}-{index + 1:03d}",
    #         name=template["name"],
    #         severity=template["severity"],
    #         description=template["description"],
    #     )
    #     for template in SIDE_EFFECT_TEMPLATES[: 2 + (index % 2)]
    # ]

    side_effect_count = randint(0, 3)
    selected_templates = sample(SIDE_EFFECT_TEMPLATES, k=side_effect_count)

    implant.side_effects = [
        SideEffectModel(
            reference=f"{template['reference']}-{index + 1:03d}",
            name=template["name"],
            severity=template["severity"],
            description=template["description"],
        )
        for template in selected_templates
    ]

    return implant


def serialize_implant(implant: ImplantModel) -> Implant:
    prerequisites_data = dict(implant.prerequisites or {})
    prerequisites_data["incompatibleImplants"] = [
        incompatible.reference for incompatible in implant.incompatible_implants
    ]

    return Implant(
        reference=implant.reference,
        name=implant.name,
        description=implant.description,
        category=implant.category,
        prerequisites=Prerequisites(**prerequisites_data),
        sideseffects=[
            {
                "reference": side_effect.reference,
                "name": side_effect.name,
                "severity": side_effect.severity.value,
                "description": side_effect.description,
            }
            for side_effect in implant.side_effects
        ],
    )


def assign_incompatibilities(implants: list[ImplantModel]) -> None:
    seen_pairs: set[tuple[str, str]] = set()

    for implant in implants:
        implant.incompatible_implants = []

    for index, implant in enumerate(implants):
        for offset in (1, 7, 13, 19, 25):
            candidate = implants[(index + offset) % len(implants)]
            if candidate.reference == implant.reference:
                continue

            pair = tuple(sorted((implant.reference, candidate.reference)))
            if pair in seen_pairs:
                continue

            seen_pairs.add(pair)
            implant.incompatible_implants.append(candidate)
            candidate.incompatible_implants.append(implant)

            if len(implant.incompatible_implants) >= 2:
                break

def seed_implants() -> None:
    with SessionLocal() as db:
        with SessionLocal() as db:
            if db.query(ImplantModel).count() >= IMPLANT_COUNT:
                return

            implants = [build_implant(index) for index in range(IMPLANT_COUNT)]
            assign_incompatibilities(implants)

            db.add_all(implants)
            db.commit()