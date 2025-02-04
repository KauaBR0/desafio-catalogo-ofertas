# Mercado Livre Catalog Scraper

Este projeto é um web scraper construído com Django e Selenium que extrai informações de produtos do site do Mercado Livre e as armazena em um banco de dados PostgreSQL. Ele também fornece uma interface web simples para visualizar e filtrar os produtos coletados.

## Funcionalidades

*   **Scraping de produtos**: Extrai informações detalhadas de produtos do Mercado Livre, incluindo nome, preço, URL, imagem, tipo de entrega e frete grátis.
*   **Armazenamento de dados**: Salva os dados coletados em um banco de dados PostgreSQL.
*   **Interface web**: Permite visualizar os produtos em uma interface web com opções de filtragem por frete grátis e entrega "Full".
*   **Destaques**: Exibe o maior e o menor preço, bem como o maior desconto entre os produtos listados.
*   **Prevenção de detecção**: Utiliza técnicas para evitar a detecção e o bloqueio pelo Mercado Livre, como a rotação de user-agents e a inclusão de atrasos aleatórios.
*   **Registro de erros**: Faz uso de logging para registrar erros durante o processo de scraping.
*   **Página de debug**: Salva a página HTML em caso de erros para facilitar a depuração.

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

*   **`catalog/`**: Contém a aplicação Django principal.
    *   **`management/commands/`**: Contém o comando personalizado `scrape_mercado_livre.py` que realiza o scraping.
    *   **`migrations/`**: Contém os arquivos de migração do banco de dados.
    *   **`templates/catalog/`**: Contém o template HTML para a interface web.
    *   **`admin.py`**: Configurações do Django Admin (atualmente vazio).
    *   **`apps.py`**: Configuração da aplicação `catalog`.
    *   **`models.py`**: Define o modelo `Product` para armazenar os dados dos produtos.
    *   **`tests.py`**: Arquivo para testes (atualmente vazio).
    *   **`urls.py`**: Define as URLs da aplicação.
    *   **`views.py`**: Define as views da aplicação, incluindo a lógica para a interface web.
*   **`debug/`**: Contém arquivos HTML salvos para depuração em caso de erros.
*   **`mercado_catalog/`**: Contém os arquivos de configuração do projeto Django.
*   **`manage.py`**: Utilitário de linha de comando do Django.

## Requisitos

*   Python 3.x
*   Django 3.2.25
*   Selenium
*   PostgreSQL

## Configuração

1. **Instalar dependências**:

    ```bash
    pip install -r requirements.txt
    ```

    (Certifique-se de ter criado e ativado um ambiente virtual antes de executar este comando).
2. **Configurar o banco de dados**:
    *   Crie um banco de dados PostgreSQL chamado `postgres`.
    *   Edite o arquivo `mercado_catalog/settings.py` e configure as credenciais do banco de dados (nome, usuário, senha, host e porta) na seção `DATABASES`.
3. **Executar migrações**:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

## Execução

1. **Executar o scraping**:

    ```bash
    python manage.py scrape_mercado_livre
    ```

    Este comando irá iniciar o scraper e coletar os dados dos produtos.
2. **Iniciar o servidor de desenvolvimento**:

    ```bash
    python manage.py runserver
    ```
3. **Acessar a interface web**:
    Abra o seu navegador e acesse `http://127.0.0.1:8000/`.

## Notas

*   O comando `scrape_mercado_livre.py` está configurado para buscar por "computador-gamer-i7-16gb-ssd-1tb".
*   Os arquivos HTML de debug são salvos no diretório `debug/` com o nome `debug_<timestamp>.html`.
*   A interface web é simples e focada em demonstrar a funcionalidade do projeto.

