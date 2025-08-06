

# **An Architectural Analysis of a Hybrid DLT for a Sovereign, Post-Quantum Economy**

## **Introduction: Aligning Philosophy with Resilient Architecture**

This report serves as an in-depth validation and strategic analysis of the proposed dual-loop economic architecture. It acknowledges the foundational insight that the substrate for a global, fungible asset must differ fundamentally from that of a high-context, relational gift economy. The analysis proceeds with a rigorous technical evaluation, treating the project's philosophical framework—the "Sacred Weave" and "Living Treasury"—not as mere branding, but as the primary design specification against which all technical choices are measured.

The objective is to move beyond preliminary research to provide a definitive, data-driven recommendation for each architectural component: the Outer Loop post-quantum (PQC) substrate, the Inner Loop relational fabric, and the "Alchemical Converter" bridge. This analysis is conducted through the specific, practical lens of implementation and long-term maintenance within a NixOS-defined, declaratively managed environment. The central thesis of this report is that the proposed hybrid architecture is not only technically sound but philosophically coherent, representing a sophisticated and resilient model for a sovereign digital economy. The primary challenges lie not in the high-level design but in the specific implementation choices and the rigorous security required for the central bridge component that alchemically links the two economic loops.

## **Part I: A Rigorous Evaluation of Post-Quantum Substrates for the Outer Loop**

The selection of a foundational ledger for the SPK token and the Living Treasury is a decision with generational consequences. It must provide an immutable, globally accessible source of truth that remains secure against cryptographic threats that are not yet fully realized. This section provides a deep, comparative analysis of the three proposed PQC blockchain candidates, substantiating and expanding upon the initial assessment with extensive data.

### **1.1. The Post-Quantum Imperative: A Foundational Analysis**

#### **Deconstructing the "Harvest Now, Decrypt Later" Threat Vector**

The imperative for post-quantum cryptography is not a speculative future concern; it is a present-day data security vulnerability. The "harvest now, decrypt later" attack vector posits that a sufficiently resourced adversary, such as a state-level actor, is actively intercepting and storing vast quantities of encrypted data today.1 This data, secured by current public-key cryptographic standards like Elliptic Curve Digital Signature Algorithm (ECDSA)—the foundation of Bitcoin, Ethereum, and nearly all contemporary blockchains—is secure for now.2

However, the advent of a cryptographically relevant quantum computer, capable of executing Shor's algorithm, will render these standards obsolete.4 At that point, any previously harvested data can be retrospectively decrypted. For a system like the Living Treasury, designed for the "Long Now," this means that the entire history of transactions, account balances, and any associated sensitive data could be compromised. This threat model makes the adoption of PQC a non-negotiable act of architectural responsibility for any system with a multi-decade or multi-generational time horizon.6 The transition to PQC must begin now to protect the confidentiality and integrity of data against this future threat.8

#### **NIST Standardization and the Cryptographic Primitives of the Next Generation**

Addressing the quantum threat requires a coordinated, global effort to develop and standardize new cryptographic algorithms. The U.S. National Institute of Standards and Technology (NIST) has led this effort through its multi-year PQC Standardization process, which invited cryptographers worldwide to submit and peer-review candidate algorithms.2 This rigorous, transparent process culminated in the publication of the first set of finalized PQC standards in August 2024, including ML-KEM (CRYSTALS-Kyber) for key encapsulation and ML-DSA (CRYSTALS-Dilithium) for digital signatures.6

These selected algorithms, primarily based on the mathematical hardness of lattice problems, represent the global consensus on the most secure and well-vetted quantum-resistant primitives available.4 Adherence to these NIST standards is a powerful risk mitigation strategy. It signals that a project is leveraging cryptography that has withstood years of intense public scrutiny from the world's leading experts, rather than relying on bespoke, proprietary, or less-vetted algorithms whose security properties are not as well understood.12 For the Outer Loop, alignment with the NIST standards should be considered a primary selection criterion.

### **1.2. Candidate Analysis: QANplatform**

#### **PQC Implementation: The Strengths of CRYSTALS-Dilithium and QAN XLINK**

QANplatform's primary strength is its proactive and standards-aligned approach to post-quantum security. The platform implements CRYSTALS-Dilithium, the lattice-based algorithm that NIST ultimately selected as its primary standard for digital signatures.6 Notably, QANplatform selected and integrated this algorithm

*before* NIST's final recommendation was published, demonstrating significant foresight and deep expertise within their technical team.6

This PQC implementation is not merely theoretical; it is embodied in a specific technology called QAN XLINK. This feature functions as a quantum-resistant cross-signer, allowing accounts to be secured with PQC signatures. This provides a concrete and 100% successful migration path for assets when quantum computers become a practical threat to traditional elliptic curve cryptography, a critical feature that many existing blockchains lack.6 This direct, standards-based approach strongly addresses the core security requirement for the Living Treasury.

#### **Security Posture: A Review of the Hacken QVM Audit Findings**

A project's commitment to security is best measured by its willingness to undergo rigorous, independent, third-party audits. QANplatform has subjected its core innovation, the QAN Virtual Machine (QVM), to a comprehensive security audit by Hacken, a reputable and ISO-certified blockchain security firm.16

The audit was particularly notable for its methodology. Faced with the complexity of the QVM—the first blockchain VM designed to deterministically execute Linux ELF binaries—Hacken developed a custom, AI-powered threat modeling tool.17 This tool drafted plausible attack scenarios and evaluated over 2,800 test cases, uncovering 22 potential issues related to non-determinism, all of which were subsequently fixed by the QANplatform team.16 This public audit provides a significant degree of assurance regarding the security and correctness of QANplatform's core execution engine, a level of validation that is not publicly available for the other candidates' novel components.

#### **Architecture and Performance: The PoR Vision vs. the PoS Reality**

QANplatform's long-term vision includes a novel consensus mechanism called Proof-of-Randomness (PoR). PoR is designed to be a highly democratic and eco-friendly algorithm that eliminates the need for complex, energy-intensive computations.18 By selecting block validators through a verifiably random process, PoR aims to allow validation on low-power hardware, such as a mobile phone or a Raspberry Pi, thereby combining the decentralization benefits of Proof-of-Work (PoW) with the energy efficiency of Proof-of-Stake (PoS).18

However, a critical dissonance exists between this vision and the platform's current implementation. The official documentation explicitly states that due to PoR's "highly experimental nature," the QAN MainNet Beta will launch with a standard Proof-of-Stake (PoS) consensus mechanism.18 Further development of PoR is contingent on user demand and is tentatively scheduled for 2025\.18 This creates a significant gap between the project's marketing and its delivered technology. While PoS is vastly more energy-efficient than PoW 21, it does not fulfill the unique ecological and decentralization promise of PoR. Therefore, any decision to adopt QANplatform must be based on the merits of a PQC-enabled, EVM-compatible PoS chain, which is a more conventional and less differentiated offering. The platform's "Hyperpolyglot" capability, allowing smart contracts in any Linux-compatible language, is a practical advantage for developer onboarding but does not alter this fundamental reality.16

#### **NixOS Integration Assessment**

The core QANplatform stack is written primarily in the Go programming language.6 From a NixOS packaging perspective, this is highly advantageous. The Nix Packages collection (Nixpkgs) has mature, robust support for building Go applications via the

buildGoModule function.25 This builder automates the process of fetching and hashing Go module dependencies from a

go.mod file, ensuring a fully deterministic and reproducible build that aligns perfectly with the core principles of Nix.26 The ease of packaging Go applications makes QANplatform a low-friction candidate for integration into a NixOS-based development and deployment pipeline.

### **1.3. Candidate Analysis: IOTA**

#### **Architectural Paradigm: The Tangle's Alignment with "Mycelial Web" Principles**

IOTA's fundamental data structure, the Tangle, is a Directed Acyclic Graph (DAG), which represents the strongest philosophical and architectural alignment with the "Mycelial Web" and "flow" principles of the project's vision.29 Unlike a traditional blockchain, which processes transactions sequentially into discrete blocks, a DAG is a blockless structure where individual transactions are directly interwoven.30 To issue a new transaction, a node must validate two previous transactions, creating a web of confirmations that grows in parallel.31

This structure mirrors the interconnected, non-linear, and flowing nature of mycelial networks. It enables feeless microtransactions and high throughput, as the network's capacity theoretically scales with the number of transactions being processed.29 This inherent parallelism and biomimetic structure make IOTA a uniquely resonant candidate for the project's underlying ethos.

#### **PQC Trajectory: From WOTS+ to Future-Proofing the DAG**

IOTA has a historical foundation in post-quantum cryptography. Early versions of the protocol used the Winternitz One-Time Signature (WOTS+) scheme, a hash-based signature that is inherently resistant to attacks by quantum computers.10 This demonstrates a long-standing awareness of the quantum threat within the project.

However, WOTS+ is an older-generation PQC scheme with significant usability limitations, most notably the requirement that an address key can only be used to sign a single outgoing transaction. While the broader cryptographic community and regulatory bodies are moving decisively toward the new NIST standards 33, the provided research materials reveal a significant information vacuum regarding IOTA's current and future PQC strategy. There are no recent, official roadmaps, technical papers, or blog posts from the IOTA Foundation that detail their plan for transitioning to next-generation PQC algorithms.33 It is unclear whether they plan to adopt NIST standards like CRYSTALS-Dilithium or pursue another path. This opacity represents a critical uncertainty for a project where long-term security is paramount.

#### **Ecological Profile: A Quantitative Look at Energy Efficiency**

The Tangle's consensus mechanism, which does not involve competitive mining like PoW, makes IOTA an extremely energy-efficient DLT.39 A single transaction on a DAG-based ledger can consume orders of magnitude less energy than a PoW transaction and is competitive with the most efficient PoS systems.30 A 2022 research report focusing on the energy consumption of the IOTA 2.0 GoShimmer prototype network confirms that energy optimization is an active area of research and a core tenet of the protocol's design.39 This strong ecological profile aligns perfectly with the project's value of "Astro-Ecological Responsibility."

#### **NixOS Integration Assessment**

The IOTA 2.0 node software is being developed in Go and Rust.40 As with QANplatform, these are ideal languages for the NixOS ecosystem. Nixpkgs provides first-class support for both languages through the mature

buildGoModule and buildRustCrate builders, which facilitate highly reproducible and deterministic builds.25 The process of building an IOTA node from source is well-documented, involving standard

cargo build commands, making it a straightforward candidate for encapsulation within a Nix derivation.40 This technical compatibility makes IOTA an excellent fit for the project's specified development environment.

### **1.4. Candidate Analysis: The xx network**

#### **Privacy by Design: A Technical Deep-Dive into cMix Metadata Shredding**

The xx network's most profound alignment with the project's vision lies in its foundational commitment to privacy, specifically the shredding of metadata. While standard encryption protects the *content* of a communication, it leaves the *metadata*—who is talking to whom, when, and from where—exposed to traffic analysis. The xx network's cMix protocol is a high-latency mixnet designed to break this link, providing a much deeper form of sovereignty and privacy.44

The cMix protocol operates in two phases. First, in a **precomputation phase**, a randomly selected team of nodes performs computationally expensive, quantum-resistant cryptographic operations to establish shared keys and a "template" for how a batch of messages will be processed.45 Second, in the

**real-time phase**, incoming messages are processed using fast symmetric-key operations. Each node in the team uses the precomputed template to re-encrypt and shuffle the order of messages in the batch before passing it to the next node.45 By the time the batch exits the team, an external observer cannot correlate the input messages with the output messages, thus "shredding" the metadata trail.45 This deep commitment to privacy is highly resonant with the "Sovereign Vessel" principle.

#### **PQC Primitives: Analyzing the Custom Hash-Based Signatures and xxBFT Consensus**

The xx network was designed from the ground up to be quantum-resistant; PQC is not an added feature but a core architectural principle.44 The xxBFT consensus protocol explicitly avoids standard public-key primitives like RSA and ECDSA. Instead, it relies on hash-based cryptographic primitives, which are generally believed to be secure against quantum computers.47 The consensus whitepaper specifically mentions the use of hash-based signatures like the Winternitz OTS+ scheme and assumes that all inter-node communication is protected by symmetric ciphers.47 This PQC-native approach ensures that the ledger's integrity is protected against both classical and quantum adversaries from its genesis.

#### **Security Posture: Assessing a Bespoke Approach in the Absence of Public Audits**

The xx network's reliance on a bespoke, custom-designed consensus protocol and cryptographic primitives presents a significant security trade-off. While these systems were designed by a world-class team with deep expertise, including cryptography pioneer David Chaum, novel cryptography is notoriously difficult to design and implement correctly.12 The history of cryptography is littered with clever designs that contained subtle, fatal flaws discovered only after years of public scrutiny.48

The provided materials contain no evidence of a comprehensive, independent, third-party security audit of the xx network's novel cryptographic primitives, such as its specific implementation of hash-based signatures or the xxBFT consensus logic.50 This stands in stark contrast to QANplatform's publicly available audit report and the global peer-review process that validated the NIST-selected algorithms. For a system intended to serve as a "Long Now" treasury, relying on unaudited, bespoke cryptography introduces a substantial and potentially unacceptable level of risk.

#### **NixOS Integration Assessment: Navigating the Complexities of C/C++ Derivations**

The xx network's node software is a polyglot codebase, comprising C, C++, and Go.54 While the Go components can be packaged straightforwardly, creating robust and reproducible Nix derivations for complex C/C++ projects can be a significant undertaking.55 C/C++ projects often rely on intricate build systems like CMake or Autotools and may have dependencies on system libraries (e.g., BLAS, OpenSSL, MPI) that require careful configuration of compiler and linker flags (

NIX\_CFLAGS\_COMPILE, NIX\_LDFLAGS) within the Nix environment to ensure they are discovered correctly.55 While entirely achievable, this represents a higher technical hurdle and a greater long-term maintenance burden compared to the self-contained, statically-linked nature of typical Go and Rust projects.58

### **1.5. Comparative Analysis and Strategic Recommendation for the Outer Loop**

The selection of the PQC substrate for the Outer Loop involves a complex trade-off between pragmatic security, philosophical alignment, and technical risk. The following matrix synthesizes the analysis of the three candidates across key decision-making criteria.

| Metric | QANplatform | IOTA | xx network |
| :---- | :---- | :---- | :---- |
| **PQC Approach** | NIST Standard Lattice-based (CRYSTALS-Dilithium) via QAN XLINK cross-signer. 6 | Historical use of Hash-based (WOTS+). Future PQC roadmap is currently undefined in public documentation. 10 | PQC-native design using custom Hash-based primitives (e.g., WOTS+) and symmetric ciphers. 47 |
| **Core Language/Stack** | Go, Solidity (EVM-compatible). 6 | Go, Rust. 40 | C, C++, Go. 54 |
| **NixOS Packaging Ease** | **High.** Mature buildGoModule builder provides excellent reproducibility. 25 | **High.** Mature buildGoModule and buildRustCrate builders provide excellent reproducibility. 43 | **Moderate.** C/C++ components require more complex derivations and dependency management. 55 |
| **Vision Alignment** | **Moderate-High.** Strong on security and practicality. Dissonance on ecological claims (PoR vs. PoS). 18 | **Very High.** DAG architecture is a direct metaphor for the "Mycelial Web." Strong ecological profile. 29 | **Very High.** Metadata-shredding privacy provides the deepest form of sovereignty. 44 |
| **Consensus Mechanism** | Proof-of-Stake (PoS) at launch, with a "highly experimental" Proof-of-Randomness (PoR) in the future. 18 | Tangle (DAG) with a future consensus mechanism replacing the Coordinator. 31 | Nominated Proof-of-Stake (NPoS) with xxBFT for finality. 44 |
| **Energy Profile** | **Low.** Consistent with standard PoS systems. 21 | **Very Low.** DAG architecture avoids mining and is highly efficient. 39 | **Low.** Consistent with standard NPoS systems. 60 |
| **Security Audit Status** | **Public.** QVM audited by Hacken, uncovering and fixing 22 issues. 16 | **No Public PQC Audit.** No publicly available audits for its future PQC implementation. 36 | **No Public Primitives Audit.** No publicly available audits of its novel cryptographic primitives. 50 |
| **Governance Model** | Primarily enterprise-focused, with partnerships with entities like IBM and the Linux Foundation. 14 | Led by the IOTA Foundation, a German non-profit, with a focus on institutional and governmental partnerships. 62 | On-chain governance via a DAO, a Council, and a Technical Committee. 59 |
| **Development Maturity** | TestNet is live. MainNet Beta launch is pending. 24 | IOTA 2.0 (Stardust) is in development, aiming to remove the centralized Coordinator. 64 | MainNet has been live since November 2021\. 60 |
| **Primary Risk Factor** | **Vision-Reality Gap:** The flagship PoR consensus mechanism is experimental and not part of the initial launch. | **PQC Roadmap Opacity:** Lack of clear, public information on the next-generation PQC strategy. | **Bespoke Cryptography:** Reliance on novel, unaudited cryptographic primitives introduces significant security risk. |

#### **Strategic Recommendation**

Based on this analysis, the strategic recommendation is multi-faceted:

1. **For Immediate, Low-Risk Development:** **QANplatform** emerges as the most pragmatic and lowest-risk choice for initial development and deployment. Its use of a NIST-standard PQC algorithm, coupled with a public, third-party security audit of its core virtual machine, provides the highest degree of cryptographic assurance at this time. The ease of packaging its Go-based stack for NixOS further reduces implementation friction. The primary compromise is the gap between its long-term PoR vision and its initial PoS reality.  
2. **For Highest Philosophical Alignment:** **IOTA** remains the most compelling candidate from an architectural and philosophical standpoint. Its DAG structure is a beautiful technical analog to the "Mycelial Web." However, the current opacity of its next-generation PQC roadmap presents an unacceptable level of uncertainty for a foundational treasury. **A strong recommendation is to actively engage with the IOTA Foundation to seek clarity on their PQC transition plan.** If they were to announce a clear, timely roadmap for implementing NIST-standard PQC algorithms, IOTA would become the leading candidate.  
3. **For Long-Term Research:** **The xx network** offers a profound vision of privacy that aligns deeply with the project's goals. However, the security risk associated with its unaudited, bespoke cryptographic primitives is too great to accept for the foundational layer of the Living Treasury. It should be relegated to a parallel research track, with its node software packaged and monitored, but not adopted as the primary substrate until its core cryptography has undergone extensive independent security analysis and validation.

## **Part II: Holochain as the Substrate for the Sacred, Relational Fabric**

The selection of Holochain for the Inner Loop's sacred, relational economy is not merely a suitable choice; it is an exceptionally precise one. Holochain's architecture is a direct technical implementation of the core principles of individual sovereignty, biomimicry, and mutual credit that define this economic layer.

### **2.1. Agent-Centricity as Architectural Sovereignty**

#### **Technical Underpinnings: The DHT, Local Source Chains, and Peer Validation**

Holochain fundamentally inverts the data-centric model of a blockchain.65 Instead of a single, global ledger that all participants must agree upon, a Holochain application (hApp) is a network of individual agents, each of whom maintains their own local, immutable, hash-chained record of their actions—their "source chain".66 This is the literal embodiment of the "Individual Sovereignty" and "Local-First" principles.

Data intended for public sharing is published to a shared Distributed Hash Table (DHT), a concept borrowed from peer-to-peer technologies like BitTorrent.67 When an agent publishes data, a random subset of their peers receives it, validates it against the application's "DNA" (the rules of the game), and stores it on the publisher's behalf.68 This peer validation mechanism creates a system of mutual accountability without requiring global consensus for every action, making it vastly more scalable and efficient.65

#### **Biomimicry in Practice**

The architecture of Holochain is explicitly modeled on living systems.65 The DHT acts as a collective memory or a shared energetic field for the application's community. The validation rules encoded in the DNA are analogous to the genetic code of an organism, defining the valid states and interactions within the system. The network of peers, each validating a small portion of the public data, functions as a distributed immune system.69 When an agent attempts to publish invalid data, the peers who receive it reject it and can gossip about the malicious actor, building a collective reputational awareness that isolates bad actors over time.68 This biomimetic approach is a perfect technical match for the "Mycelial Kosmos" and "Living Systems" metaphors that guide the project's vision.

### **2.2. The Nature of Value in Holochain: Mutual Credit and Reputation Systems**

#### **Beyond Fungibility: A Feature, Not a Bug**

The most critical distinction for the Inner Loop is that Holochain is not designed to support a native, global, fungible token. This is a deliberate architectural choice. Holochain is optimized for creating contextual, non-fungible, and relational "current-sees".70 Its agent-centric structure is ideal for implementing mutual-credit systems, where currency is created not by a central mint but through the act of extending credit between peers within a bounded community.71

This makes Holochain the uniquely perfect substrate for the Inner Loop's economic primitives:

* The non-transferable **WIS (Wisdom) score** is a reputational currency, reflecting an agent's contributions.  
* The community-care **HEART token** is likely a form of mutual credit, issued and accepted based on trust and relationships.  
* The multidimensional **Springs** (Water, Light, Seed) represent flows of specific, non-fungible value types.

Holochain provides the native tools and architectural patterns to build these high-context, relational value systems without attempting to force them into the rigid, low-context model of a fungible blockchain token.69

#### **Case Studies and Implementations**

The Holochain ecosystem has a strong and growing focus on enabling these alternative economic models. The Holochain Foundation itself launched a wholly-owned business, **Unyt, Inc.**, in 2025 with the specific mission of developing a mutual-credit accounting engine for decentralized infrastructure use-cases.73

Furthermore, the open-source **"Community Mutual Credit hApp"** serves as a key reference implementation and learning tool.71 This project demonstrates core patterns essential for building relational economies on Holochain, such as:

* **Social Triangulation:** A mechanism where existing members of a DHT must "vouch" for a new agent before they are allowed to join, creating a web-of-trust membrane.  
* **The Lobby Pattern:** A public DHT space where prospective members can interact with existing members to request vouches, bridging the gap between the "outside" and the trusted "inside" of the community.

These existing tools and open-source projects provide a solid foundation and concrete, reusable patterns for building the Inner Loop's Sacred Reciprocity system.71

### **2.3. Development and Deployment within a Declarative Ecosystem**

#### **The Holonix Environment and Community-Maintained Nix Flakes**

Holochain's alignment with the project's technical stack is exceptionally strong. The official development environment for Holochain is **Holonix**, a Nix-based environment that provides all the necessary compilers, dependencies, and tooling for a specific Holochain release.77 The official installation script for developers sets up the Nix package manager and configures a binary cache (

cachix) to avoid lengthy local compilations.79

Crucially, the Holochain development workflow has fully embraced Nix Flakes, the modern, reproducible way of managing Nix projects.78 The scaffolding tool,

hc-scaffold, now generates a flake.nix file by default when creating a new project.78 This allows a developer to enter a perfectly configured, sandboxed development environment with a single command:

nix develop. While the original holochain-nixpkgs repository has been deprecated, all Nix-related development has been consolidated into the main Holochain repository, signaling a deep and ongoing commitment to the Nix ecosystem.82 This makes Holochain the candidate with the highest degree of compatibility and lowest friction for the project's specified NixOS-based environment.

## **Part III: The Synthesis: A Resilient Hybrid Architecture for a Two-Loop Economy**

The proposed hybrid architecture, which uses distinct DLT paradigms for its two economic loops, is a sophisticated and robust design. The integrity of this entire system, however, hinges on the security and trustworthiness of the bridge that connects them—the "Alchemical Converter."

### **3.1. The "Alchemical Converter": An Analysis of Bridge Architectures**

#### **Oracles vs. Multi-Signature Schemes: A Security and Decentralization Trade-off Analysis**

The proposal for an "Oracular Council" using "multi-signature validation" correctly identifies the core mechanism for the bridge. It is essential to understand that a multi-signature scheme is not an *alternative* to an oracle; it is a specific *implementation* of a trusted, federated oracle.83

* A **Multi-Signature (Multi-Sig) Scheme** requires a threshold of M out of N pre-selected signers to approve a transaction. Its security relies on the cryptographic soundness of the signature scheme and, more importantly, on the operational security and integrity of the N key holders.84 It is centralized around this chosen set of actors.  
* A **Decentralized Oracle Network (DON)**, such as Chainlink, attempts to decentralize this trust by using a large, dynamic set of independent node operators who are crypto-economically incentivized (through staking and rewards) to report data honestly.86 Security emerges from the assumption that it would be prohibitively expensive for an attacker to bribe or compromise a sufficient number of independent nodes.87

For the "Alchemical Converter," a multi-signature council is a pragmatic and appropriate choice. It provides a clear chain of accountability. However, this design concentrates trust and risk in the council members and their governance process. The security of the bridge is not just a technical problem but a social and political one. The entire system is only as decentralized and secure as this centralizing component.

#### **Bridging Paradigms: Challenges and Patterns for Connecting Agent-Centric and Global Ledger Systems**

The architectural challenge of this bridge is significant. It must translate a state from the Inner Loop—a high-context, subjective reality distributed across a peer-to-peer network—into a low-context, objective fact that can be immutably recorded on the Outer Loop's global ledger.88 For example, the statement "Agent Alice has a WIS score of 100" is a conclusion derived from observing and validating many individual actions within the Holochain DHT. The bridge's function is to have a trusted entity attest to this conclusion, triggering a corresponding

mint(Alice, amount) transaction on the PQC blockchain.

A practical pattern for this can be adapted from Holo's own infrastructure. The **Holo Web Bridge** is a service that provides a standard HTTP API endpoint for querying data from a Holochain DHT.90 The members of the Oracular Council could run services that use this pattern to read the necessary WIS scores from the Inner Loop. They would then independently sign a message attesting to these scores, and once a threshold of signatures is collected, a final transaction would be submitted to the PQC blockchain to execute the SPK token distribution.

### **3.2. Architectural Validation and Strategic Refinements**

#### **Validating the Two-Loop Model**

The proposed hybrid architecture is not only valid but represents an elegant and mature design pattern. It correctly applies the principle of "using the right tool for the right purpose." It avoids the common architectural anti-pattern of trying to force a single DLT paradigm—be it a blockchain or an agent-centric framework—to handle all types of value and interaction. By separating the fungible, low-context "body" of the economy from the relational, high-context "soul," the architecture is more resilient, more efficient, and more truthful to the nature of the reality it seeks to model.88

#### **Recommendations for Securing the Oracular Council Bridge Mechanism**

Given that the bridge is the most critical point of centralization and trust in the system, its design and governance must be exceptionally robust. The following strategic refinements are recommended:

* **Cryptographic Implementation:** Implement a robust multi-signature scheme with a high security threshold (e.g., requiring signatures from more than two-thirds of the council members). If the chosen PQC blockchain supports it, a Schnorr-based multi-signature scheme would be preferable, as it allows for key aggregation, which can reduce on-chain verification costs and enhance privacy.83  
* **Governance Protocol:** Define and implement a clear, transparent, and ideally on-chain governance process for adding and removing members of the Oracular Council. This process should itself be governed by the broader community of SPK token holders or another defined stakeholder group.  
* **Operational Security:** Mandate stringent operational security practices for all council members. This must include the use of hardware security modules (HSMs) or other secure key storage solutions to prevent the compromise of individual private keys.48  
* **Time-Delayed Execution and Challenge Periods:** To mitigate the risk of a compromised or colluding council executing a malicious transaction, implement a time-delay mechanism. When the council submits an attestation to the PQC blockchain (e.g., for a "Flourishing Airdrop"), the corresponding transaction should enter a pending state for a defined "challenge period." During this period, the transaction details would be publicly visible, allowing the broader community to scrutinize them and potentially vote to veto the transaction if it is deemed fraudulent. This adds a crucial layer of social oversight to the technical security of the bridge.

## **Conclusion and Strategic Roadmap**

### **4.1. Concluding Assessment: An Elegant and Truthful Architecture**

The proposed dual-loop, hybrid DLT architecture is a sophisticated, resilient, and philosophically coherent design. It correctly maps distinct technological paradigms to the distinct economic realities they are intended to support: a secure, permanent, universal substrate for the livelihood economy and a fluid, agent-centric, living substrate for the gift economy. The analysis confirms the validity of this high-level design. The primary challenges and risks lie not in the overarching concept but in the detailed execution: the careful selection of a PQC substrate based on a trade-off between assurance and alignment, and the paramount importance of designing a provably secure and socially legitimate bridge to link the two worlds.

### **4.2. Actionable Research and Development Roadmap**

The following is a proposed, phased roadmap to move from architectural validation to implementation.

#### **Immediate Priorities (0-3 Months)**

* **Nix Flake Development and Benchmarking:**  
  * Begin immediate development of Nix flakes for the **QANplatform testnet** and the **IOTA 2.0 testnet** node software. Leverage the buildGoModule and buildRustCrate builders for deterministic builds.25  
  * The primary goal is to deploy these nodes as reproducible NixOS services.93  
  * Establish a benchmarking suite to measure stability, resource consumption (CPU, RAM, disk I/O), and transaction finality under various load conditions.  
* **Holochain Prototyping:**  
  * Utilize the official Holonix flake via nix develop "github:holochain/holonix?ref=main-0.5" to establish the development environment.78  
  * Begin prototyping the core Inner Loop hApps, focusing on the data structures and validation rules for the WIS score and HEART token, drawing from patterns in the "Community Mutual Credit hApp".71

#### **Mid-Term Goals (3-9 Months)**

* **PQC Substrate Selection:**  
  * Based on the results of the benchmarking and a formal request for information to the IOTA Foundation regarding their PQC roadmap, make a final selection for the Outer Loop substrate.  
* **"Alchemical Converter" Bridge Prototyping:**  
  * Design and build a prototype of the bridge.  
  * **Phase 1:** Implement a simple M-of-N multi-signature wallet contract on the chosen PQC testnet.  
  * **Phase 2:** Develop a trusted off-chain service (the "oracle client") that runs on a secure server. This service will query the Holochain hApp's API (using a pattern similar to the Holo Web Bridge 90) to retrieve WIS scores.  
  * **Phase 3:** Integrate the oracle client with the multi-sig contract, allowing it to propose and sign attestations that trigger token distributions on the testnet.  
* **xx network Research Track:**  
  * As a parallel effort, commence the more complex task of packaging the xx network node for NixOS. This will involve crafting a robust Nix derivation that correctly handles its C/C++ build system and dependencies.55 The goal is to have a functional node for long-term observation and potential future integration.

#### **Long-Term Vision (9+ Months)**

* **Security Audits:**  
  * Commission independent, professional security audits for all custom-built components, with the highest priority on the "Alchemical Converter" bridge contracts and off-chain services.  
* **Governance Formalization:**  
  * Formalize and deploy the on-chain governance contracts and off-chain operational procedures for the Oracular Council, including member selection and the challenge/veto mechanism.  
* **Mainnet Deployment:**  
  * Plan and execute a phased rollout to the selected mainnets, beginning with the deployment of the SPK token contract and the Living Treasury, followed by the activation of the bridge and the first "Flourishing Airdrop." This path forward provides a structured approach to realizing the project's ambitious and worthy vision.

#### **Works cited**

1. Preparing for Post Quantum Cryptography \- Oracle Blogs, accessed August 1, 2025, [https://blogs.oracle.com/security/post/post-quantum-cryptography](https://blogs.oracle.com/security/post/post-quantum-cryptography)  
2. Quantum Threats to Blockchain: How Bitcoin & Ethereum Are Adapting | Fireblocks, accessed August 1, 2025, [https://www.fireblocks.com/blog/how-blockchains-will-evolve-for-the-quantum-era/](https://www.fireblocks.com/blog/how-blockchains-will-evolve-for-the-quantum-era/)  
3. Post-Quantum Crypto Agility \- Thales CPL, accessed August 1, 2025, [https://cpl.thalesgroup.com/encryption/post-quantum-crypto-agility](https://cpl.thalesgroup.com/encryption/post-quantum-crypto-agility)  
4. What is Post-Quantum Cryptography (PQC)? \- Palo Alto Networks, accessed August 1, 2025, [https://www.paloaltonetworks.com/cyberpedia/what-is-post-quantum-cryptography-pqc](https://www.paloaltonetworks.com/cyberpedia/what-is-post-quantum-cryptography-pqc)  
5. \[2403.11741\] Post-Quantum Cryptography: Securing Digital Communication in the Quantum Era \- arXiv, accessed August 1, 2025, [https://arxiv.org/abs/2403.11741](https://arxiv.org/abs/2403.11741)  
6. Quantum-resistant Security \- QANplatform, accessed August 1, 2025, [https://learn.qanplatform.com/technology/technology-features/quantum-resistant-security](https://learn.qanplatform.com/technology/technology-features/quantum-resistant-security)  
7. Preparing your organization for the quantum threat to cryptography (ITSAP.00.017), accessed August 1, 2025, [https://www.cyber.gc.ca/en/guidance/preparing-your-organization-quantum-threat-cryptography-itsap00017](https://www.cyber.gc.ca/en/guidance/preparing-your-organization-quantum-threat-cryptography-itsap00017)  
8. Post-quantum cryptography in Red Hat Enterprise Linux 10, accessed August 1, 2025, [https://www.redhat.com/en/blog/post-quantum-cryptography-red-hat-enterprise-linux-10](https://www.redhat.com/en/blog/post-quantum-cryptography-red-hat-enterprise-linux-10)  
9. NIST Post-Quantum Cryptography Standardization \- Wikipedia, accessed August 1, 2025, [https://en.wikipedia.org/wiki/NIST\_Post-Quantum\_Cryptography\_Standardization](https://en.wikipedia.org/wiki/NIST_Post-Quantum_Cryptography_Standardization)  
10. Post-quantum cryptography \- Wikipedia, accessed August 1, 2025, [https://en.wikipedia.org/wiki/Post-quantum\_cryptography](https://en.wikipedia.org/wiki/Post-quantum_cryptography)  
11. ISTANBUL TECHNICAL UNIVERSITY ELECTRICAL-ELECTRONICS FACULTY SENIOR DESIGN PROJECT JANUARY 2024 SYSTEM ON CHIP DESIGN FOR POST-Q, accessed August 1, 2025, [https://web.itu.edu.tr/\~orssi/thesis/2024/EkinErdogan\_bit.pdf](https://web.itu.edu.tr/~orssi/thesis/2024/EkinErdogan_bit.pdf)  
12. Cryptographic primitive \- Wikipedia, accessed August 1, 2025, [https://en.wikipedia.org/wiki/Cryptographic\_primitive](https://en.wikipedia.org/wiki/Cryptographic_primitive)  
13. Cryptography \- Trail of Bits, accessed August 1, 2025, [https://www.trailofbits.com/services/software-assurance/cryptography/](https://www.trailofbits.com/services/software-assurance/cryptography/)  
14. QANplatform Joins Linux Foundation and its Post-Quantum Cryptography Alliance, accessed August 1, 2025, [https://thequantuminsider.com/2024/10/09/qanplatform-joins-linux-foundation-and-its-post-quantum-cryptography-alliance/](https://thequantuminsider.com/2024/10/09/qanplatform-joins-linux-foundation-and-its-post-quantum-cryptography-alliance/)  
15. Technology Features \- QANplatform, accessed August 1, 2025, [https://learn.qanplatform.com/technology/technology-features](https://learn.qanplatform.com/technology/technology-features)  
16. QANplatform's Core Innovation, the QVM Passes Security Audit | by ..., accessed August 1, 2025, [https://medium.com/qanplatform/qanplatforms-core-innovation-the-qvm-passes-security-audit-e6dad138207e](https://medium.com/qanplatform/qanplatforms-core-innovation-the-qvm-passes-security-audit-e6dad138207e)  
17. Hacken & QANplatform Launch AI-Powered Threat Modeling Tool \- Medium, accessed August 1, 2025, [https://medium.com/qanplatform/hacken-qanplatform-launch-ai-powered-threat-modeling-tool-12d01aea0e3e](https://medium.com/qanplatform/hacken-qanplatform-launch-ai-powered-threat-modeling-tool-12d01aea0e3e)  
18. Proof-of-Randomness (PoR) consensus algorithm \- QANplatform, accessed August 1, 2025, [https://learn.qanplatform.com/technology/technology-features/proof-of-randomness-por-consensus-algorithm](https://learn.qanplatform.com/technology/technology-features/proof-of-randomness-por-consensus-algorithm)  
19. Mobile Phone Validation | QANplatform, accessed August 1, 2025, [https://learn.qanplatform.com/technology/technology-features/mobile-phone-validation](https://learn.qanplatform.com/technology/technology-features/mobile-phone-validation)  
20. Developers | QAN blockchain platform \- QANplatform, accessed August 1, 2025, [https://qanplatform.com/en/developers](https://qanplatform.com/en/developers)  
21. What Does Proof-of-Stake (PoS) Mean in Crypto? \- Investopedia, accessed August 1, 2025, [https://www.investopedia.com/terms/p/proof-stake-pos.asp](https://www.investopedia.com/terms/p/proof-stake-pos.asp)  
22. Proof of Stake (PoS) vs. Proof of Work (PoW) \- Hedera, accessed August 1, 2025, [https://hedera.com/learning/consensus-algorithms/proof-of-stake-vs-proof-of-work](https://hedera.com/learning/consensus-algorithms/proof-of-stake-vs-proof-of-work)  
23. Is Proof-of-Stake Really More Energy-Efficient Than Proof-of-Work? \- Bitwave, accessed August 1, 2025, [https://www.bitwave.io/blog/is-proof-of-stake-really-more-energy-efficient-than-proof-of-work](https://www.bitwave.io/blog/is-proof-of-stake-really-more-energy-efficient-than-proof-of-work)  
24. QAN blockchain platform \- QANplatform, accessed August 1, 2025, [https://qanplatform.com/en](https://qanplatform.com/en)  
25. Go \- NixOS Wiki, accessed August 1, 2025, [https://nixos.wiki/wiki/Go](https://nixos.wiki/wiki/Go)  
26. Nix & NixOS | Declarative builds and deployments, accessed August 1, 2025, [https://nixos.org/](https://nixos.org/)  
27. How Nix Works \- NixOS, accessed August 1, 2025, [https://nixos.org/guides/how-nix-works/](https://nixos.org/guides/how-nix-works/)  
28. Help packaging go project \- NixOS Discourse, accessed August 1, 2025, [https://discourse.nixos.org/t/help-packaging-go-project/42906](https://discourse.nixos.org/t/help-packaging-go-project/42906)  
29. DAG vs. Blockchain: They Are Not as Different as You Think. \- Aleph Zero, accessed August 1, 2025, [https://alephzero.org/blog/dag-vs-blockchain-they-are-not-as-different-as-you-think/](https://alephzero.org/blog/dag-vs-blockchain-they-are-not-as-different-as-you-think/)  
30. DAG vs Blockchain: Comparing Efficiency, Scalability and Use Cases \- CrustLab, accessed August 1, 2025, [https://crustlab.com/blog/dag-vs-blockchain/](https://crustlab.com/blog/dag-vs-blockchain/)  
31. IOTA (technology) \- Wikipedia, accessed August 1, 2025, [https://en.wikipedia.org/wiki/IOTA\_(technology)](https://en.wikipedia.org/wiki/IOTA_\(technology\))  
32. Suhail, S., Hussain, R., Khan, A., & Hong, C. S. (2020). On the Role of Hash-Based Signatures in Quantum-Safe Internet of Th \- University of Bristol Research Portal, accessed August 1, 2025, [https://research-information.bris.ac.uk/files/308852441/2004.10435v1.pdf](https://research-information.bris.ac.uk/files/308852441/2004.10435v1.pdf)  
33. A Coordinated Implementation Roadmap for the Transition to Post ..., accessed August 1, 2025, [https://digital-strategy.ec.europa.eu/en/library/coordinated-implementation-roadmap-transition-post-quantum-cryptography](https://digital-strategy.ec.europa.eu/en/library/coordinated-implementation-roadmap-transition-post-quantum-cryptography)  
34. PQC Migration Roadmap \- Post-Quantum Cryptography Coalition |, accessed August 1, 2025, [https://pqcc.org/post-quantum-cryptography-migration-roadmap/](https://pqcc.org/post-quantum-cryptography-migration-roadmap/)  
35. (PQC) Post-Quantum Cryptography Blog Category \- DigiCert, accessed August 1, 2025, [https://www.digicert.com/blog/category/post-quantum-cryptography](https://www.digicert.com/blog/category/post-quantum-cryptography)  
36. IOTA | Built to Make a Difference, accessed August 1, 2025, [https://www.iota.org/](https://www.iota.org/)  
37. IOTA Blog, accessed August 1, 2025, [https://blog.iota.org/](https://blog.iota.org/)  
38. arXiv.org e-Print archive, accessed August 1, 2025, [https://arxiv.org/](https://arxiv.org/)  
39. \[2210.13996\] Report on the energy consumption of the IOTA 2.0 prototype network (GoShimmer 0.8.3) under different testing scenarios \- arXiv, accessed August 1, 2025, [https://arxiv.org/abs/2210.13996](https://arxiv.org/abs/2210.13996)  
40. Systemd Setup | IOTA Documentation, accessed August 1, 2025, [https://docs.iota.org/operator/validator-node/systemd](https://docs.iota.org/operator/validator-node/systemd)  
41. Build From Source \- IOTA Documentation, accessed August 1, 2025, [https://docs.iota.org/operator/full-node/source](https://docs.iota.org/operator/full-node/source)  
42. Learn Nix \- NixOS, accessed August 1, 2025, [https://nixos.org/learn/](https://nixos.org/learn/)  
43. nixpkgs/doc/languages-frameworks/rust.section.md at master \- GitHub, accessed August 1, 2025, [https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/rust.section.md](https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/rust.section.md)  
44. Blockchain \- xx network Quantum-Resistant-Decentralized-Blockchain, accessed August 1, 2025, [https://xx.network/quantum-resistant-decentralized-blockchain/](https://xx.network/quantum-resistant-decentralized-blockchain/)  
45. cMix \- xx network, accessed August 1, 2025, [https://xx.network/wp-content/uploads/2021/10/xxcMixwhitepaper.pdf](https://xx.network/wp-content/uploads/2021/10/xxcMixwhitepaper.pdf)  
46. cMix: Mixing with Minimal Real-Time Asymmetric Cryptographic Operations | Request PDF, accessed August 1, 2025, [https://www.researchgate.net/publication/318162121\_cMix\_Mixing\_with\_Minimal\_Real-Time\_Asymmetric\_Cryptographic\_Operations](https://www.researchgate.net/publication/318162121_cMix_Mixing_with_Minimal_Real-Time_Asymmetric_Cryptographic_Operations)  
47. xx network \- White Paper xx consensus, accessed August 1, 2025, [https://xx.network/wp-content/uploads/2021/10/xx-consensus-whitepaper.pdf](https://xx.network/wp-content/uploads/2021/10/xx-consensus-whitepaper.pdf)  
48. How to Conduct a Crypto Security Audit? \- SentinelOne, accessed August 1, 2025, [https://www.sentinelone.com/cybersecurity-101/cybersecurity/crypto-security-audit/](https://www.sentinelone.com/cybersecurity-101/cybersecurity/crypto-security-audit/)  
49. Where's Crypto?: Automated Identification and Classification of Proprietary Cryptographic Primitives in Binary Code | USENIX, accessed August 1, 2025, [https://www.usenix.org/conference/usenixsecurity21/presentation/meijer](https://www.usenix.org/conference/usenixsecurity21/presentation/meijer)  
50. xx network: Quantum Resistant Decentralized Mixnet with Blockchain, accessed August 1, 2025, [https://xx.network/](https://xx.network/)  
51. accessed December 31, 1969, [https://xx.network/security/](https://xx.network/security/)  
52. Network Security Audit | Audit Checklist & Best Practices \- Darktrace, accessed August 1, 2025, [https://www.darktrace.com/cyber-ai-glossary/how-to-conduct-a-network-security-audit](https://www.darktrace.com/cyber-ai-glossary/how-to-conduct-a-network-security-audit)  
53. Three Year Chain Audit \- General \- xx network Forum, accessed August 1, 2025, [https://forum.xx.network/t/three-year-chain-audit/7036](https://forum.xx.network/t/three-year-chain-audit/7036)  
54. xxfoundation/xxchain: xx network Substrate based blockchain node \- GitHub, accessed August 1, 2025, [https://github.com/xx-labs/xxchain](https://github.com/xx-labs/xxchain)  
55. C \- NixOS Wiki, accessed August 1, 2025, [https://nixos.wiki/wiki/C](https://nixos.wiki/wiki/C)  
56. Hacking Your First Package — nix-tutorial documentation \- GitLab Inria, accessed August 1, 2025, [https://nix-tutorial.gitlabpages.inria.fr/nix-tutorial/first-package.html](https://nix-tutorial.gitlabpages.inria.fr/nix-tutorial/first-package.html)  
57. Nixpkgs Reference Manual \- NixOS, accessed August 1, 2025, [https://nixos.org/nixpkgs/manual/](https://nixos.org/nixpkgs/manual/)  
58. How do I install C/C++ on NixOS \- Reddit, accessed August 1, 2025, [https://www.reddit.com/r/NixOS/comments/175c5o6/how\_do\_i\_install\_cc\_on\_nixos/](https://www.reddit.com/r/NixOS/comments/175c5o6/how_do_i_install_cc_on_nixos/)  
59. Overview | xx Network Docs, accessed August 1, 2025, [https://learn.xx.network/xxchain/](https://learn.xx.network/xxchain/)  
60. Mission \- xx network, accessed August 1, 2025, [https://xx.network/mission/](https://xx.network/mission/)  
61. QANplatform \- Cyber Security Intelligence, accessed August 1, 2025, [https://www.cybersecurityintelligence.com/qanplatform-10580.html](https://www.cybersecurityintelligence.com/qanplatform-10580.html)  
62. IOTA Foundation Targets 30-Country Expansion via Government Partnerships Tangle Tech, accessed August 1, 2025, [https://www.ainvest.com/news/iota-foundation-targets-30-country-expansion-government-partnerships-tangle-tech-2507/](https://www.ainvest.com/news/iota-foundation-targets-30-country-expansion-government-partnerships-tangle-tech-2507/)  
63. \*\*\*Important note to reader: this document is a courtesy English translation of the IOTA Foundation's official charter. The, accessed August 1, 2025, [https://files.iota.org/comms/IOTA+Foundation+Charter+final.pdf](https://files.iota.org/comms/IOTA+Foundation+Charter+final.pdf)  
64. IOTA Smart Contracts \- GitHub, accessed August 1, 2025, [https://raw.githubusercontent.com/iotaledger/wasp/develop/documentation/ISC\_WP\_Nov\_10\_2021.pdf](https://raw.githubusercontent.com/iotaledger/wasp/develop/documentation/ISC_WP_Nov_10_2021.pdf)  
65. Holochain Core Concepts: What is Holochain?, accessed August 1, 2025, [https://developer.holochain.org/concepts/](https://developer.holochain.org/concepts/)  
66. Holochain vs Blockchain: A New Vision for Web3, with HOT Price Forecast \- Gate.com, accessed August 1, 2025, [https://www.gate.com/crypto-wiki/article/holochain-vs-blockchain-a-new-vision-for-web3-with-hot-price-forecast](https://www.gate.com/crypto-wiki/article/holochain-vs-blockchain-a-new-vision-for-web3-with-hot-price-forecast)  
67. Holochain \- P2P Foundation Wiki, accessed August 1, 2025, [https://wiki.p2pfoundation.net/Holochain](https://wiki.p2pfoundation.net/Holochain)  
68. Holochain | Distributed app framework with P2P networking, accessed August 1, 2025, [https://www.holochain.org/](https://www.holochain.org/)  
69. Projects \- Holochain, accessed August 1, 2025, [https://www.holochain.org/projects/](https://www.holochain.org/projects/)  
70. Holochain: an agent-centric framework for distributed apps \- Ethereum Research, accessed August 1, 2025, [https://ethresear.ch/t/holochain-an-agent-centric-framework-for-distributed-apps/5153](https://ethresear.ch/t/holochain-an-agent-centric-framework-for-distributed-apps/5153)  
71. Play with a mutual credit currency and join the modularity discussion \- Holochain Blog, accessed August 1, 2025, [https://blog.holochain.org/play-with-a-mutual-credit-currency-and-join-the-modularity-discussion/](https://blog.holochain.org/play-with-a-mutual-credit-currency-and-join-the-modularity-discussion/)  
72. A New Type of Cryptocurrency, As Old As Civilisation \- Holochain Blog, accessed August 1, 2025, [https://blog.holochain.org/mutual-credit-part-1-a-new-type-of-cryptocurrency-as-old-as-civilisation/](https://blog.holochain.org/mutual-credit-part-1-a-new-type-of-cryptocurrency-as-old-as-civilisation/)  
73. The Foundation \- Holochain, accessed August 1, 2025, [https://www.holochain.org/foundation/](https://www.holochain.org/foundation/)  
74. Holochain · GitHub, accessed August 1, 2025, [https://github.com/holochain/](https://github.com/holochain/)  
75. Holochain Forum \- Learn, Discuss, Collaborate, accessed August 1, 2025, [https://forum.holochain.org/](https://forum.holochain.org/)  
76. Holochain Open Development · GitHub, accessed August 1, 2025, [https://github.com/holochain-open-dev/](https://github.com/holochain-open-dev/)  
77. Tools and Libraries \- Holochain, accessed August 1, 2025, [https://www.holochain.org/tools-and-libraries/](https://www.holochain.org/tools-and-libraries/)  
78. Setup with Nix flakes \- Holochain Developer Portal, accessed August 1, 2025, [https://developer.holochain.org/get-started/install-advanced/](https://developer.holochain.org/get-started/install-advanced/)  
79. Requirements: Setup \- Holochain Gym, accessed August 1, 2025, [https://holochain-gym.github.io/developers/requirements/setup/](https://holochain-gym.github.io/developers/requirements/setup/)  
80. Get Started \- Holochain Developer Portal, accessed August 1, 2025, [https://developer.holochain.org/get-started/](https://developer.holochain.org/get-started/)  
81. holochain/holonix: Holochain app development ... \- GitHub, accessed August 1, 2025, [https://github.com/holochain/holonix](https://github.com/holochain/holonix)  
82. holochain/holochain-nixpkgs \- GitHub, accessed August 1, 2025, [https://github.com/holochain/holochain-nixpkgs](https://github.com/holochain/holochain-nixpkgs)  
83. A Decentralized Oracle Network Constructed From Weighted Schnorr Multisignature, accessed August 1, 2025, [https://www.researchgate.net/publication/388868639\_A\_Decentralized\_Oracle\_Network\_Constructed\_From\_Weighted\_Schnorr\_Multisignature](https://www.researchgate.net/publication/388868639_A_Decentralized_Oracle_Network_Constructed_From_Weighted_Schnorr_Multisignature)  
84. Decentralized MPC vs Multisig \- Qredo, accessed August 1, 2025, [https://www.qredo.com/blog/decentralized-mpc-vs-multisig](https://www.qredo.com/blog/decentralized-mpc-vs-multisig)  
85. Guardians | Wormhole Docs, accessed August 1, 2025, [https://wormhole.com/docs/protocol/infrastructure/guardians/](https://wormhole.com/docs/protocol/infrastructure/guardians/)  
86. Seven Key Cross-Chain Bridge Vulnerabilities Explained \- Chainlink, accessed August 1, 2025, [https://chain.link/education-hub/cross-chain-bridge-vulnerabilities](https://chain.link/education-hub/cross-chain-bridge-vulnerabilities)  
87. Types of Blockchain Oracle Attacks, Cases, and Multi-Layer Defense Strategies, accessed August 1, 2025, [https://www.gate.com/learn/articles/types-of-blockchain-oracle-attacks-cases-and-multi-layer-defense-strategies/5498](https://www.gate.com/learn/articles/types-of-blockchain-oracle-attacks-cases-and-multi-layer-defense-strategies/5498)  
88. “Distributed Ledgers: Innovation and Regulation in Financial Infrastructure and Payment Systems” Robert M. Townsend\* Elizabe, accessed August 1, 2025, [https://www.riksbank.se/globalassets/media/konferenser/2018/distributed-ledgers---innovation-and-regulation-in-financial-infrastructure-and-payment-systems.pdf](https://www.riksbank.se/globalassets/media/konferenser/2018/distributed-ledgers---innovation-and-regulation-in-financial-infrastructure-and-payment-systems.pdf)  
89. Reimagining New Socio-Technical Economics Through ... \- Frontiers, accessed August 1, 2025, [https://www.frontiersin.org/journals/blockchain/articles/10.3389/fbloc.2019.00029/full](https://www.frontiersin.org/journals/blockchain/articles/10.3389/fbloc.2019.00029/full)  
90. Introducing Cloud Nodes \+ Web Bridge for Holochain Applications | Blog \- Holo Host, accessed August 1, 2025, [https://holo.host/blog/introducing-cloud-nodes-web-bridge-for-holochain-7WCp2eKjHD4/](https://holo.host/blog/introducing-cloud-nodes-web-bridge-for-holochain-7WCp2eKjHD4/)  
91. Holo, accessed August 1, 2025, [https://holo.host/](https://holo.host/)  
92. Improving the scalability of blockchain through DAG \- ResearchGate, accessed August 1, 2025, [https://www.researchgate.net/publication/337580877\_Improving\_the\_scalability\_of\_blockchain\_through\_DAG](https://www.researchgate.net/publication/337580877_Improving_the_scalability_of_blockchain_through_DAG)  
93. nixos-config/flake.nix at main \- GitHub, accessed August 1, 2025, [https://github.com/mitchellh/nixos-config/blob/main/flake.nix](https://github.com/mitchellh/nixos-config/blob/main/flake.nix)  
94. nixos-anywhere/flake.nix at main \- GitHub, accessed August 1, 2025, [https://github.com/nix-community/nixos-anywhere/blob/main/flake.nix](https://github.com/nix-community/nixos-anywhere/blob/main/flake.nix)