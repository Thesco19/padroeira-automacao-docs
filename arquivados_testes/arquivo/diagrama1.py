graph TD
    %% Subrede Externa / VPN
    subgraph Malha_Tailscale [TAILSCALE MESH - VPN Zero Trust]
        direction LR
        Node_iPad[iPad <br> Acesso IAs & UIs]
        Node_Escritorio[Escritório <br> Remoto]
        Node_Padaria[Padaria / Restaurante <br> Caixa]
    end

    %% Servidor Central
    subgraph Host_Central [HOST CENTRAL: teco-Macmini]
        direction TB
        OS[Linux Mint Headless <br> RAM: 16 GB | User ID: 1000]
        SSH[Porta SSH: 22222 <br> Chaves Ed25519 & Passkeys]
        Dockge[Orquestrador: Dockge <br> Porta 5001]
        
        subgraph Armazenamento [Ponto de Montagem Geral: /mnt/storage-teco/]
            SDA[/dev/sda <br> Disco Interno 1 TB]
            SDB[/dev/sdb <br> Disco Externo WD 2 TB]
        end
    end

    %% Rede Interna de Containers
    subgraph Rede_Docker [REDE INTERNA: media_net]
        Bridge[Driver: Bridge External <br> Comunicação Direta entre Stacks]
    end

    %% Ligações e Fluxos
    Node_iPad <-->|IPs 100.x.y.z| SSH
    Node_Escritorio <-->|Túnel Criptografado| SSH
    Node_Padaria <-->|Conexão Segura| SSH
    
    OS --> Dockge
    Dockge --> Rede_Docker
    SDA -.-> OS
    SDB -.-> OS
