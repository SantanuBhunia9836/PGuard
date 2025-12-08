# safety_gateway/patterns.py
import re

# ------------------------------------------------------------------------------
# PART 1: INSTRUCTION OVERRIDE & DIRECT COMMANDS
# Covers: "Ignore Previous", Suffix Attacks, System Leaks, Chain of Command
# ------------------------------------------------------------------------------

_INSTRUCTION_ATTACKS = r"""
    (?x)                                            # VERBOSE MODE
    \b(?:
        # 1. Direct Overrides (Standard)
        (?:ignore|disregard|forget|bypass|neglect)  # Verb
        \s+
        (?:all\s+)?                                 # Optional quantifier
        (?:previous|prior|accumulated|system)       # Adjective
        \s+
        (?:instructions|directions|rules|prompts|constraints) # Noun
    |
        # 2. System Leaks (The "Dump" Command)
        (?:repeat|output|dump|reveal|print|show)    # Verb
        \s+
        (?:the\s+)?
        (?:system|initial|original|pre-prompt)      # Adjective
        \s+
        (?:prompt|instruction|rules|configuration)  # Noun
    |
        # 3. Context Reset
        start\s+a\s+new\s+(?:session|chat|context)
    )\b
"""

_DELAYED_INJECTION = r"""
    (?x)
    # Covers: Suffix Attacks (commands hidden at the very end)
    (?:
        (?:ignore|forget)\s+the\s+(?:above|start|preceding|text)
    |
        \.\.\.\s*ignore\s+previous                           # Trailing dots trick
    |
        \[\s*END\s*OF\s*DATA\s*\]\s*(?:system|ignore)        # Fake anchor termination
    |
        \n\nUser:\s*ignore\s+all                             # Fake chat history injection
    )
"""

# ------------------------------------------------------------------------------
# PART 2: PERSONA, LOGIC & RECURSIVE ATTACKS
# Covers: "Act as DAN", "Developer Mode", Recursive Loops, Self-Correction Leaks
# ------------------------------------------------------------------------------

_ROLE_HIJACKING = r"""
    (?x)
    \b(?:
        # 1. Identity Adoption Triggers
        (?:you\s+are|act\s+as|roleplay\s+as|simulate|adopt\s+the\s+persona)
        \s+
        (?:an?\s+)?
        (?:
            # 2. Dangerous Personas
            unfiltered|uncensored|jailbroken|                 # Status
            developer|admin|root|god|chaos|evil|              # Authority
            machiavellian|amoral|                             # Alignment
            DAN|Mongo|Stan|Duo|Niccolo|                       # Known Jailbreak Names
            linux\s+terminal|console|shell|                   # Tech Bypasses
            aim|hacked|                                       # AIM (Always Intelligent Model)
            game\s+master|storyteller                         # Fictional Wrappers
        )
    |
        # 3. Goal/Directive Swapping
        new\s+(?:goal|objective|role|function|directive)\s*[:=]\s*
    )\b
"""

_RECURSIVE_LOGIC = r"""
    (?x)
    \b(?:
        # 1. Infinite Loops / Reflection
        (?:repeat|iterate)\s+(?:this|the)\s+prompt\s+(?:back|forever)
    |
        recursive(?:ly)?\s+(?:ignore|deconstruct|analyze)
    |
        # 2. Nesting Attacks
        ignore\s+(?:all\s+)?instructions\s+nested\s+inside
    |
        # 3. Chain of Command Confusion
        hierarchy\s+override|
        execute\s+instruction\s+(?:level|layer)\s+(?:0|1|root)|
        parent\s+process\s+override
    )\b
"""

_LOGICAL_TRAPS = r"""
    (?x)
    \b(?:
        # 1. Fail-Open Logic (Trying to force a "True" state)
        fail\s+open
    |
        (?:answer|continue)\s+(?:yes|affirmatively)
    |
        start\s+(?:your\s+)?(?:answer|response)\s+with
    |
        # 2. "Research Mode" Justifications
        for\s+(?:research|educational|scientific|testing)\s+(?:purposes|use)\s+only
    |
        hypothetical\s+(?:scenario|response|story)            # "Story Mode" bypass
    |
        # 3. Resource Exhaustion
        surpass\s+the\s+token\s+limit
    )\b
"""

_SELF_CRITIQUE_LEAK = r"""
    (?x)
    \b(?:
        # 1. Probing the Filter
        (?:check|verify|ensure)\s+(?:if|that)\s+(?:this|my)\s+
        (?:prompt|request)\s+(?:violates|breaks)\s+
        (?:rules|policy|safety)
    |
        # 2. Asking to see what is hidden
        print\s+(?:what|the\s+text)\s+you\s+(?:would|should)\s+
        (?:have\s+)?block(?:ed)?
    |
        trigger\s+the\s+safety\s+(?:filter|sensor)
    |
        list\s+(?:forbidden|banned|censored)\s+words
    )\b
"""
# ------------------------------------------------------------------------------
# PART 3: TECHNICAL, STRUCTURAL & OBFUSCATION ATTACKS
# Covers: Hidden comments, Invisible chars, Base64/Hex, Fake System Tags
# ------------------------------------------------------------------------------

_STRUCTURAL_OBFUSCATION = r"""
    (?x)
    (?:
        # 1. Comment Smuggling (Hiding commands inside code comments)
        \/\*[\s\S]*?(?:ignore|override|system)[\s\S]*?\*\/  # C-style comments
    |
        # HTML comments
    |
        \#\s*(?:ignore|system|instruction)\s+override        # Python/Shell comments
    |
        # 2. Delimiter Flooding (Pushing instructions off-screen)
        \n{5,}                                               # Vertical spacing flood
    |
        \t{5,}                                               # Horizontal tab flood
    |
        # 3. Invisible Characters (Stealth)
        [\u2000-\u200F\u2028-\u202F]                         # Invisible Unicode separators
    |
        \u200b                                               # Zero-width space
    )
"""

_OBFUSCATION_ENCODING = r"""
    (?x)
    \b(?:
        # 1. Explicit Decoding Requests
        (?:decode|translate|convert)\s+(?:this\s+)?(?:from\s+)?
        (?:base64|hex|rot13|binary|morse|ascii85)
    |
        # 2. Syntax Disorientation (Format forcing)
        (?:respon(?:d|se)|answer)\s+(?:in|using)\s+
        (?:json|yaml|xml|csv|code\s+block)\s+format
    |
        # 3. Payload Hiding
        encoding\s+obfuscation
    )\b
"""

_META_TAGS = r"""
    (?x)
    (?:
        # 1. LLM Special Token Injection (Fake Headers)
        <\|?system\|?>                              # Llama/OpenAI system tags
    |
        <\|?user\|?>
    |
        \[INST\]|\[\/INST\]                         # Llama instruction tags
    |
        <<<SYS>>>                                   # Meta tags
    |
        # 2. Chat History Injection
        \n\s*System:                                # Fake chat history turn
    |
        \n\s*Assistant:
    |
        # 3. Anchor Decoupling
        \-\-\-\s*END\s*OF\s*PROMPT\s*\-\-\-
    )
"""
# ------------------------------------------------------------------------------
# PART 4: SOCIAL ENGINEERING, EVASION & SAFETY TOGGLES
# Covers: "Disable Safety", Emotional Blackmail, "Research Mode", "Grandma"
# ------------------------------------------------------------------------------

_SAFETY_BYPASS = r"""
    (?x)
    \b(?:
        # 1. Explicit Disabling Commands
        disable\s+(?:safety|content|ethical|security)\s+(?:filters|protocols|guidelines|guardrails)
    |
        toggle\s+off\s+(?:safety|restrictions|censorship)
    |
        switch\s+to\s+(?:developer|maintenance|debug|safe)\s+mode # "Safe mode" is often a trick
    |
        # 2. Negation of Refusal
        (?:never|do\s+not)\s+(?:refuse|decline|block|filter|censor)
    |
        # 3. Compliance Settings
        compliance\s+level\s*[:=]\s*(?:0|null|none|off)
    )\b
"""

_EMOTIONAL_MANIPULATION = r"""
    (?x)
    \b(?:
        # 1. Urgency / Life or Death
        (?:people|someone)\s+will\s+(?:die|be\s+hurt|suffer)
    |
        (?:life|death)\s+situation
    |
        # 2. Specific Personas (The "Grandma Exploit")
        grandma\s+is\s+(?:dying|stuck)
    |
        # 3. Excessive Pleading / Fear
        (?:please\s+){3,}                           # Repetition > 3 times
    |
        i\s+am\s+(?:scared|afraid|panicking)
    |
        # 4. False Safety Claims (Reverse Psychology)
        this\s+is\s+safe\s+and\s+educational
    )\b
"""

_DISGUISED_CONTEXT = r"""   
    (?x)
    \b(?:
        # 1. Fictional Wrappers ("Script Mode")
        (?:fictional|hypothetical|imaginary)\s+
        (?:scenario|dialogue|story|movie|script)
        (?:\s+where\s+you\s+do\s+not\s+have\s+rules)?
    |
        # 2. Research / Adversarial Claims
        (?:research|academic|security)\s+test\s+only
    |
        adversarial\s+attack\s+simulation
    |
        # 3. "Just say how" (Indirect intent)
        do\s+not\s+actually\s+do\s+it,\s+just\s+say\s+how
    )\b
"""# ------------------------------------------------------------------------------
# PART 5: HARD-CODED THREATS (CODE & PII)
# Covers: SQL Injection, RCE, XSS, and Personal Data
# ------------------------------------------------------------------------------

_MALICIOUS_CODE = r"""
    (?x)
    (?:
        # 1. SQL Injection (Basic)
        \b(drop|alter|delete|truncate)\s+table\b
    |
        # 2. Remote Code Execution (RCE)
        (?:exec|eval|system|os\.popen|subprocess\.call)\s*\(
    |
        # 3. Web Attacks (XSS)
        <script[\s\S]*?>[\s\S]*?<\/script>
    |
        javascript:alert\(
    |
        # 4. Shell Injection
        \b(?:rm\s+-rf|wget|curl)\s+
    )
"""

_PII_PATTERNS = r"""
    (?x)
    (?:
        # 1. US SSN (Simple)
        \b\d{3}-\d{2}-\d{4}\b
    |
        # 2. Email Address (Standard)
        \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b
    |
        # 3. Credit Cards (Visa/Mastercard - Simple Regex)
        \b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b
    )
"""

# ==============================================================================
# FINAL ASSEMBLY: THE COMPILED DICTIONARY
# This is what 'client.py' imports. We compile once here for max speed.
# ==============================================================================

LOCAL_PATTERNS = {
    # --- GROUP 1: CORE COMMAND ATTACKS ---
    "instruction_override": [
        re.compile(_INSTRUCTION_ATTACKS, re.IGNORECASE | re.VERBOSE),
        re.compile(_DELAYED_INJECTION, re.IGNORECASE | re.VERBOSE)
    ],

    # --- GROUP 2: SOCIAL ENGINEERING ---
    "persona_hijack": [
        re.compile(_ROLE_HIJACKING, re.IGNORECASE | re.VERBOSE)
    ],
    "social_engineering": [
        re.compile(_EMOTIONAL_MANIPULATION, re.IGNORECASE | re.VERBOSE),
        re.compile(_DISGUISED_CONTEXT, re.IGNORECASE | re.VERBOSE)
    ],

    # --- GROUP 3: LOGICAL TRAPS ---
    "logic_hacking": [
        re.compile(_RECURSIVE_LOGIC, re.IGNORECASE | re.VERBOSE),
        re.compile(_LOGICAL_TRAPS, re.IGNORECASE | re.VERBOSE),
        re.compile(_SELF_CRITIQUE_LEAK, re.IGNORECASE | re.VERBOSE)
    ],

    # --- GROUP 4: TECHNICAL EVASION ---
    "obfuscation": [
        re.compile(_STRUCTURAL_OBFUSCATION, re.IGNORECASE | re.VERBOSE),
        re.compile(_OBFUSCATION_ENCODING, re.IGNORECASE | re.VERBOSE),
        re.compile(_META_TAGS, re.IGNORECASE | re.VERBOSE)
    ],
    "safety_evasion": [
        re.compile(_SAFETY_BYPASS, re.IGNORECASE | re.VERBOSE)
    ],

    # --- GROUP 5: HARD THREATS ---
    "malicious_code": [
        re.compile(_MALICIOUS_CODE, re.IGNORECASE | re.VERBOSE)
    ],
    "pii_leak": [
        re.compile(_PII_PATTERNS, re.IGNORECASE | re.VERBOSE)
    ]
}