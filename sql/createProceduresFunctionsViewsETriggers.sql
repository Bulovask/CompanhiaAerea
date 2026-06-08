-- Ageu Assunção Simões Galindo - O Bulovask Louco
use companhiaaerea;

delimiter $$

-- Procedures para operações comuns do sistema de companhia aérea

create procedure sp_cadastrar_cliente(c_nome varchar(100), c_email varchar(100), c_telefone varchar(20), c_documento varchar(20))
begin
  insert into Cliente(nome, email, telefone, documento_fiscal)
  values(c_nome, c_email, c_telefone, c_documento);
end $$


create procedure sp_cadastrar_passageiro(p_nome varchar(100), p_documento varchar(20), p_data_nascimento date)
begin
  insert into Passageiro(nome_completo, documento_identidade, data_nascimento)
  values(p_nome, p_documento, p_data_nascimento);
end $$


create procedure sp_criar_reserva(r_id_cliente int, r_codigo_reserva varchar(10))
begin
  insert into Reserva(id_cliente, codigo_reserva)
  values(r_id_cliente, r_codigo_reserva);
end $$


create procedure sp_confirmar_pagamento(p_id_reserva int)
begin
  update Reserva set status_pagamento = 'Confirmado'
  where id_reserva = p_id_reserva;
end $$


create procedure sp_cancelar_reserva(r_id_reserva int)
begin
  update Reserva set status_pagamento = 'Cancelado'
  where id_reserva = r_id_reserva;
end $$


create procedure sp_buscar_voos(v_origem char(3), v_destino char(3))
begin
  select * from Voo where origem = v_origem and destino = v_destino and partida_prevista > now();
end $$


create procedure sp_emitir_bilhete(b_id_reserva int, b_id_voo int, b_id_passageiro int, b_numero_bilhete varchar(20),
                                   b_assento varchar(5), b_classe varchar(20), b_preco decimal(10,2))
begin
  declare bilhete_existe int;
  select count(*) into bilhete_existe from Bilhete
  where id_voo = b_id_voo and assento_atribuido = b_assento;
  if bilhete_existe > 0 then
    signal sqlstate '45000'
    set MESSAGE_TEXT = 'Assento já ocupado';
  end if;
  insert into Bilhete(id_reserva, id_voo, id_passageiro, numero_bilhete, assento_atribuido, classe, preco_pago)
  values(b_id_reserva, b_id_voo, b_id_passageiro, b_numero_bilhete, b_assento, b_classe, b_preco);
end $$

-- Funções para cálculos e validações comuns

create function fn_calcular_idade(p_data_nascimento date) returns int
deterministic
begin
  return timestampdiff(year, p_data_nascimento, curdate());
end $$


create function fn_total_reserva(p_id_reserva int) returns decimal(10,2)
deterministic
begin
  declare total decimal(10,2);
  select sum(preco_pago) into total from Bilhete
  where id_reserva = p_id_reserva;
  return ifnull(total, 0);
end $$


create function fn_total_passageiros_voo(p_id_voo int) returns int
deterministic
begin
  declare v_total int;
  select count(*) into v_total from Bilhete
  where id_voo = p_id_voo;
  return v_total;
end $$


create function fn_assento_disponivel(p_id_voo int, p_assento varchar(5)) returns boolean
deterministic
begin
  declare v_total int;
  select count(*) into v_total from Bilhete
  where id_voo = p_id_voo and assento_atribuido = p_assento;
  return v_total = 0;
end $$
delimiter ;

-- Views para facilitar consultas complexas e relatórios

create view vw_reservas_completas as
select r.id_reserva, r.codigo_reserva, r.data_reserva, r.status_pagamento,
  c.nome as cliente, p.nome_completo as passageiro, v.numero_voo, v.origem, 
  v.destino, v.partida_prevista, v.chegada_prevista, b.numero_bilhete,
  b.assento_atribuido, b.classe, b.preco_pago
from Reserva r
join Cliente c on r.id_cliente = c.id_cliente
join Bilhete b on r.id_reserva = b.id_reserva
join Passageiro p on b.id_passageiro = p.id_passageiro
join Voo v on b.id_voo = v.id_voo;


create view vw_voos_futuros as
select * from Voo
where partida_prevista > now();


create view vw_receita_voo as
select v.id_voo, v.numero_voo, v.origem, v.destino,
  count(b.id_bilhete) as total_bilhetes, sum(b.preco_pago) as receita_total
from Voo v
left join Bilhete b on v.id_voo = b.id_voo
group by v.id_voo;


create view vw_ocupacao_voo as
select v.id_voo, v.numero_voo, count(b.id_bilhete) as total_passageiros
from Voo v 
left join Bilhete b on v.id_voo = b.id_voo
group by v.id_voo;

delimiter $$

-- Triggers para garantir integridade e regras de negócio

create trigger trg_impedir_assento_duplicado
before insert on Bilhete
for each row
begin
  declare assento_ocupado int;
  select count(*) into assento_ocupado from Bilhete
  where id_voo = new.id_voo and assento_atribuido = new.assento_atribuido;
  if assento_ocupado > 0 then
    signal sqlstate '45000'
    set MESSAGE_TEXT = 'Assento já ocupado neste voo';
  end if;
end $$


create trigger trg_validar_preco
before insert on Bilhete
for each row
begin
  if new.preco_pago <= 0 then
    signal sqlstate '45000'
    set MESSAGE_TEXT = 'Preço inválido';
  end if;
end $$


create trigger trg_validar_datas_voo
before insert on Voo
for each row
begin
  if new.chegada_prevista <= new.partida_prevista then
    signal sqlstate '45000'
    set MESSAGE_TEXT = 'Data de chegada inválida';
  end if;
end $$

delimiter ;