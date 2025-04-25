-- Script de configuração do banco de dados Oracle para o AgroStock Lite
-- ========================================================================
-- PARTE 1: Execute como SYS ou SYSTEM
-- ========================================================================

-- Remover usuário se já existir (opcional, descomente se necessário)
-- DROP USER agrostock CASCADE;

-- Criar usuário
CREATE USER agrostock IDENTIFIED BY agrostock123;

-- Conceder privilégios básicos
GRANT CONNECT, RESOURCE TO agrostock;
GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW TO agrostock;
GRANT CREATE SEQUENCE, CREATE TRIGGER TO agrostock;
GRANT CREATE PROCEDURE, CREATE FUNCTION TO agrostock;
GRANT CREATE SYNONYM TO agrostock;
GRANT CREATE PUBLIC SYNONYM TO agrostock;
GRANT UNLIMITED TABLESPACE TO agrostock;

-- ========================================================================
-- PARTE 2: Execute como usuário AGROSTOCK
-- ========================================================================
-- Antes de executar esta parte, conecte-se como usuário agrostock:
-- CONNECT agrostock/agrostock123

-- Criar tabela principal
CREATE TABLE INSUMOS (
    CODIGO NUMBER PRIMARY KEY,
    NOME VARCHAR2(60) NOT NULL,
    QUANTIDADE NUMBER(10,2) NOT NULL,
    UNIDADE VARCHAR2(10) NOT NULL,
    PRECO_UNIT NUMBER(10,2) NOT NULL,
    NIVEL_MIN NUMBER(10,2) NOT NULL,
    DATA_CRIACAO TIMESTAMP DEFAULT SYSTIMESTAMP,
    DATA_ATUALIZACAO TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- Criar sequência
CREATE SEQUENCE SEQ_INSUMOS
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

-- Criar triggers
CREATE OR REPLACE TRIGGER TRG_INSUMOS_UPDATE
    BEFORE UPDATE ON INSUMOS
    FOR EACH ROW
BEGIN
    :NEW.DATA_ATUALIZACAO := SYSTIMESTAMP;
END;
/

CREATE OR REPLACE TRIGGER TRG_INSUMOS_INSERT
    BEFORE INSERT ON INSUMOS
    FOR EACH ROW
BEGIN
    IF :NEW.CODIGO IS NULL THEN
        :NEW.CODIGO := SEQ_INSUMOS.NEXTVAL;
    END IF;
    :NEW.DATA_CRIACAO := SYSTIMESTAMP;
    :NEW.DATA_ATUALIZACAO := SYSTIMESTAMP;
END;
/

-- Criar índices
CREATE INDEX IDX_INSUMOS_NOME ON INSUMOS(NOME);
CREATE INDEX IDX_INSUMOS_QUANTIDADE ON INSUMOS(QUANTIDADE);

-- Inserir dados de exemplo
INSERT INTO INSUMOS (NOME, QUANTIDADE, UNIDADE, PRECO_UNIT, NIVEL_MIN) 
VALUES ('Semente de Soja', 1000.00, 'kg', 15.50, 200.00);

INSERT INTO INSUMOS (NOME, QUANTIDADE, UNIDADE, PRECO_UNIT, NIVEL_MIN) 
VALUES ('Fertilizante NPK', 500.00, 'kg', 8.75, 100.00);

INSERT INTO INSUMOS (NOME, QUANTIDADE, UNIDADE, PRECO_UNIT, NIVEL_MIN) 
VALUES ('Herbicida', 50.00, 'L', 45.90, 10.00);

COMMIT;

-- Criar views
CREATE OR REPLACE VIEW VW_INSUMOS_CRITICOS AS
    SELECT CODIGO, NOME, QUANTIDADE, UNIDADE, NIVEL_MIN
    FROM INSUMOS
    WHERE QUANTIDADE <= NIVEL_MIN;

CREATE OR REPLACE VIEW VW_RELATORIO_ESTOQUE AS
    SELECT 
        CODIGO,
        NOME,
        QUANTIDADE,
        UNIDADE,
        PRECO_UNIT,
        NIVEL_MIN,
        QUANTIDADE * PRECO_UNIT AS VALOR_TOTAL,
        CASE 
            WHEN QUANTIDADE <= NIVEL_MIN THEN 'CRÍTICO'
            WHEN QUANTIDADE <= NIVEL_MIN * 1.5 THEN 'ALERTA'
            ELSE 'NORMAL'
        END AS STATUS
    FROM INSUMOS;

-- Criar procedimento para registrar entrada
CREATE OR REPLACE PROCEDURE REGISTRAR_ENTRADA (
    p_codigo IN NUMBER,
    p_quantidade IN NUMBER
) AS
BEGIN
    UPDATE INSUMOS
    SET QUANTIDADE = QUANTIDADE + p_quantidade
    WHERE CODIGO = p_codigo;
    
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
/

-- Criar procedimento para registrar saída
CREATE OR REPLACE PROCEDURE REGISTRAR_SAIDA (
    p_codigo IN NUMBER,
    p_quantidade IN NUMBER
) AS
    v_quantidade_atual NUMBER;
BEGIN
    SELECT QUANTIDADE INTO v_quantidade_atual
    FROM INSUMOS
    WHERE CODIGO = p_codigo
    FOR UPDATE;
    
    IF v_quantidade_atual < p_quantidade THEN
        RAISE_APPLICATION_ERROR(-20001, 'Quantidade insuficiente em estoque');
    END IF;
    
    UPDATE INSUMOS
    SET QUANTIDADE = QUANTIDADE - p_quantidade
    WHERE CODIGO = p_codigo;
    
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
/

-- Criar função para verificar nível mínimo
CREATE OR REPLACE FUNCTION VERIFICAR_NIVEL_MINIMO (
    p_codigo IN NUMBER
) RETURN NUMBER AS
    v_quantidade NUMBER;
    v_nivel_min NUMBER;
BEGIN
    SELECT QUANTIDADE, NIVEL_MIN
    INTO v_quantidade, v_nivel_min
    FROM INSUMOS
    WHERE CODIGO = p_codigo;
    
    RETURN v_quantidade - v_nivel_min;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN NULL;
END;
/

-- Conceder permissões
GRANT SELECT, INSERT, UPDATE, DELETE ON INSUMOS TO PUBLIC;
GRANT SELECT ON VW_INSUMOS_CRITICOS TO PUBLIC;
GRANT SELECT ON VW_RELATORIO_ESTOQUE TO PUBLIC;
GRANT EXECUTE ON REGISTRAR_ENTRADA TO PUBLIC;
GRANT EXECUTE ON REGISTRAR_SAIDA TO PUBLIC;
GRANT EXECUTE ON VERIFICAR_NIVEL_MINIMO TO PUBLIC;

-- Criar sinônimos públicos
-- Execute apenas se necessário
CREATE PUBLIC SYNONYM INSUMOS FOR agrostock.INSUMOS;
CREATE PUBLIC SYNONYM VW_INSUMOS_CRITICOS FOR agrostock.VW_INSUMOS_CRITICOS;
CREATE PUBLIC SYNONYM VW_RELATORIO_ESTOQUE FOR agrostock.VW_RELATORIO_ESTOQUE;
CREATE PUBLIC SYNONYM REGISTRAR_ENTRADA FOR agrostock.REGISTRAR_ENTRADA;
CREATE PUBLIC SYNONYM REGISTRAR_SAIDA FOR agrostock.REGISTRAR_SAIDA;
CREATE PUBLIC SYNONYM VERIFICAR_NIVEL_MINIMO FOR agrostock.VERIFICAR_NIVEL_MINIMO;

-- ========================================================================
-- SCRIPT CONCLUÍDO
-- ======================================================================== 